import { ProductOutlined, ShopOutlined } from '@ant-design/icons';
import { Button, Flex, Form, TimePicker, Typography } from 'antd';
import dayjs from 'dayjs';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, useParams } from 'react-router';
import { DatasetForm } from '@/components/datasets/dataset-form/dataset-form.component';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    useDeleteFreshnessSloMutation,
    useGetFreshnessSloQuery,
    useGetOutputPortQuery,
    useUpsertFreshnessSloMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    ApplicationPaths,
    createDataProductIdPath,
    createMarketplaceOutputPortPath,
    createOutputPortPath,
} from '@/types/navigation.ts';

function FreshnessSloSection({ datasetId, dataProductId }: { datasetId: string; dataProductId: string }) {
    const { t } = useTranslation();
    const { data: slo } = useGetFreshnessSloQuery({ id: datasetId, dataProductId });
    const [upsertSlo] = useUpsertFreshnessSloMutation();
    const [deleteSlo] = useDeleteFreshnessSloMutation();
    const [form] = Form.useForm();

    useEffect(() => {
        form.setFieldsValue({
            deadline_time: slo?.deadline_time ? dayjs(slo.deadline_time, 'HH:mm:ss') : undefined,
        });
    }, [form, slo]);

    async function handleSave(values: { deadline_time: dayjs.Dayjs }) {
        try {
            await upsertSlo({
                dataProductId,
                id: datasetId,
                freshnessSloRequest: {
                    deadline_time: values.deadline_time.format('HH:mm:ss'),
                },
            }).unwrap();
            dispatchMessage({ content: t('Freshness SLO saved'), type: 'success' });
        } catch {
            dispatchMessage({ content: t('Failed to save Freshness SLO'), type: 'error' });
        }
    }

    async function handleDelete() {
        try {
            await deleteSlo({ dataProductId, id: datasetId }).unwrap();
            form.resetFields();
            dispatchMessage({ content: t('Freshness SLO removed'), type: 'success' });
        } catch {
            dispatchMessage({ content: t('Failed to remove Freshness SLO'), type: 'error' });
        }
    }

    return (
        <Flex vertical gap="small" style={{ marginTop: 24 }}>
            <Typography.Title level={4}>{t('Freshness SLO')}</Typography.Title>
            <Typography.Text type="secondary">
                {t('Set the daily deadline by which this output port is expected to be refreshed (UTC).')}
            </Typography.Text>
            <Form
                form={form}
                layout="inline"
                initialValues={{
                    deadline_time: slo?.deadline_time ? dayjs(slo.deadline_time, 'HH:mm:ss') : undefined,
                }}
                onFinish={handleSave}
            >
                <Form.Item
                    name="deadline_time"
                    label={t('Deadline (UTC)')}
                    rules={[{ required: true, message: t('Please select a deadline time') }]}
                >
                    <TimePicker format="HH:mm" />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit">
                        {t('Save')}
                    </Button>
                </Form.Item>
                {slo && (
                    <Form.Item>
                        <Button danger onClick={handleDelete}>
                            {t('Remove SLO')}
                        </Button>
                    </Form.Item>
                )}
            </Form>
        </Flex>
    );
}

export function DatasetEdit() {
    const { t } = useTranslation();
    const { datasetId = '', dataProductId = '' } = useParams();
    const { data, isError } = useGetOutputPortQuery(
        { id: datasetId, dataProductId },
        { skip: !datasetId || !dataProductId },
    );
    const navigate = useNavigate();

    const { pathname } = useLocation();
    const { setBreadcrumbs } = useBreadcrumbs();
    const { data: outputPort } = useGetOutputPortQuery(
        { dataProductId, id: datasetId },
        { skip: !dataProductId || !datasetId },
    );
    const { data: data_product } = useGetDataProductQuery(dataProductId, {
        skip: !dataProductId,
    });
    useEffect(() => {
        if (pathname.includes('studio')) {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            <ProductOutlined /> {t('Product Studio')}
                        </>
                    ),
                    path: ApplicationPaths.Studio,
                },
                { title: <>{data_product?.name}</>, path: createDataProductIdPath(dataProductId) },
                { title: <>{outputPort?.name}</>, path: createOutputPortPath(dataProductId, datasetId) },
                { title: <>{t('Edit')}</> },
            ]);
        } else {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            {' '}
                            <ShopOutlined /> {t('Marketplace')}
                        </>
                    ),
                    path: ApplicationPaths.Marketplace,
                },
                { title: <>{data_product?.name}</>, path: createDataProductIdPath(dataProductId) },
                { title: <>{outputPort?.name}</>, path: createMarketplaceOutputPortPath(dataProductId, datasetId) },
                { title: <>{t('Edit')}</> },
            ]);
        }
    }, [setBreadcrumbs, data_product, outputPort, dataProductId, datasetId, pathname, t]);

    if (!datasetId || isError) {
        navigate(ApplicationPaths.Marketplace, { replace: true });
        return null;
    }

    return (
        <>
            <Typography.Title level={3}>{data?.name}</Typography.Title>
            <DatasetForm mode={'edit'} datasetId={datasetId} dataProductId={dataProductId} />
            <FreshnessSloSection datasetId={datasetId} dataProductId={dataProductId} />
        </>
    );
}
