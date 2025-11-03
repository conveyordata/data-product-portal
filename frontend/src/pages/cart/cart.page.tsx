import { BellOutlined, CheckCircleOutlined, MessageOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Col, Divider, Flex, Form, type FormProps, Row, Select, Typography, theme } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';
import { CartOverview } from '@/components/cart/cart-overview.component.tsx';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { clearCart, selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import {
    useGetDataProductByIdQuery,
    useGetUserDataProductsQuery,
    useRequestDatasetsAccessForDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';

const cartFormDataStorageKey = 'cart-form-data';

export function Cart() {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const { data: datasets, isFetching: fetchingDatasets } = useGetAllDatasetsQuery();
    const [requestDatasetAccessForDataProduct, { isSuccess: requestingAccessSuccess, isLoading: isRequestingAccess }] =
        useRequestDatasetsAccessForDataProductMutation();
    const cartDatasetIds = useSelector(selectCartDatasetIds);
    const cartDatasets = useMemo(() => {
        if (cartDatasetIds.length === 0) {
            return [];
        }
        return datasets?.filter((dataset) => cartDatasetIds.includes(dataset.id));
    }, [datasets, cartDatasetIds]);

    const currentUser = useSelector(selectCurrentUser);
    const { data: userDataProducts, isFetching: isFetchingUserDataProducts } = useGetUserDataProductsQuery(
        currentUser!.id,
        {
            skip: currentUser === null,
        },
    );
    const [form] = Form.useForm<CartFormData>();
    useEffect(() => {
        const savedData = localStorage.getItem(cartFormDataStorageKey);
        if (savedData) {
            form.setFieldsValue(JSON.parse(savedData));
        }
    }, []);

    type CartFormData = {
        dataProductId?: string;
        justification?: string;
    };
    const onFinish: FormProps<CartFormData>['onFinish'] = (values) => {
        if (!values.justification || !values.dataProductId) {
            return;
        }
        requestDatasetAccessForDataProduct({
            datasetIds: cartDatasetIds,
            dataProductId: values.dataProductId!,
            justification: values.justification!,
        });
    };
    const onValuesChange: FormProps<CartFormData>['onValuesChange'] = (_, values: CartFormData) => {
        localStorage.setItem(cartFormDataStorageKey, JSON.stringify(values));
    };
    const dataProductOptions = userDataProducts?.map((dataProduct) => {
        return {
            value: dataProduct?.id,
            label: dataProduct?.name,
        };
    });
    const selectedDataProductId = Form.useWatch('dataProductId', form);

    const { data: selectedDataProduct, refetch: refetchSelectedDataProduct } = useGetDataProductByIdQuery(
        selectedDataProductId!,
        {
            skip: !selectedDataProductId,
        },
    );
    useEffect(() => {
        if (!selectedDataProduct) {
            return;
        }
        if (selectedDataProduct.id !== selectedDataProductId) {
            refetchSelectedDataProduct();
        }
    });

    const overlappingDatasetIds = useMemo(() => {
        const datasetLinks = selectedDataProduct?.dataset_links ?? [];
        return datasetLinks.filter((link) => cartDatasetIds.includes(link.dataset_id)).map((link) => link.dataset_id);
    }, [cartDatasetIds, selectedDataProduct?.dataset_links]);

    const selectedProductDatasetsInCart = useMemo(() => {
        const selectedProductDatasets = selectedDataProduct?.datasets ?? [];
        return selectedProductDatasets.filter((ds) => cartDatasetIds.includes(ds.id));
    }, [selectedDataProduct?.datasets, cartDatasetIds]);

    useEffect(() => {
        if (requestingAccessSuccess) {
            dispatch(clearCart());
            localStorage.removeItem(cartFormDataStorageKey);
            dispatchMessage({ content: t('Your requests have successfully been created.'), type: 'success' });

            navigate(createDataProductIdPath(selectedDataProductId!, DataProductTabKeys.Datasets));
        }
    }, [requestingAccessSuccess, selectedDataProductId, dispatch, navigate, t]);

    const submitFormIssues = useMemo(() => {
        const submitFormIssues = [];
        if (overlappingDatasetIds.length > 0) {
            submitFormIssues.push({
                key: 'overlappingDatasetIds',
                value: t(
                    'There are currently {{count}} output ports in the cart, for which the selected Data product already has access, or has an access request.',
                    {
                        count: overlappingDatasetIds.length,
                    },
                ),
            });
        }
        if (selectedProductDatasetsInCart.length > 0) {
            submitFormIssues.push({
                key: 'selectedProductDatasetsInCart',
                value: t(
                    'There are currently {{count}} output ports, that are part of your selected Data product, please remove them.',
                    {
                        count: selectedProductDatasetsInCart.length,
                    },
                ),
            });
        }

        return submitFormIssues;
    }, [overlappingDatasetIds, selectedProductDatasetsInCart, t]);
    return (
        <Row gutter={16}>
            <Col span={10}>
                <CartOverview
                    loading={fetchingDatasets}
                    cartDatasets={cartDatasets}
                    overlappingDatasetIds={overlappingDatasetIds}
                    footer={
                        <Flex justify={'flex-end'}>
                            {t('{{count}} output ports', {
                                count: cartDatasets?.length || 0,
                            })}
                        </Flex>
                    }
                    selectedDataProductId={selectedDataProductId}
                />
            </Col>
            <Col span={14}>
                <Card title={<Typography.Title level={3}>{t('Data checkout')}</Typography.Title>}>
                    <Form<CartFormData>
                        layout={'vertical'}
                        onFinish={onFinish}
                        form={form}
                        onValuesChange={onValuesChange}
                    >
                        <Form.Item<CartFormData>
                            name="dataProductId"
                            label={t('Data product')}
                            rules={[{ required: true, message: t('Please select a data product') }]}
                        >
                            <Select
                                showSearch
                                placeholder={t('Select a data product')}
                                options={dataProductOptions}
                                loading={isFetchingUserDataProducts}
                                filterOption={(input, option) =>
                                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                                }
                            />
                        </Form.Item>
                        {submitFormIssues.length > 0 && (
                            <Alert
                                message={t('Cannot submit request')}
                                description={
                                    <ul style={{ margin: 0, paddingLeft: 20 }}>
                                        {submitFormIssues.map((reason) => (
                                            <li key={reason.key}>{reason.value}</li>
                                        ))}
                                    </ul>
                                }
                                type="warning"
                                showIcon
                                style={{ marginBottom: 16 }}
                            />
                        )}
                        <Form.Item<FieldType>
                            name="justification"
                            label={'Business justification'}
                            rules={[
                                {
                                    required: true,
                                    message: t('Please explain why you need access to these output ports'),
                                },
                            ]}
                        >
                            <TextArea rows={4} placeholder="Explain why you need access to these output ports" />
                        </Form.Item>
                        <Form.Item label={null}>
                            <Flex gap={'small'}>
                                <Link to={ApplicationPaths.Datasets} style={{ width: '100%' }}>
                                    <Button type="default" style={{ width: '100%' }}>
                                        {t('Continue browsing')}
                                    </Button>
                                </Link>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    style={{ width: '100%' }}
                                    loading={isRequestingAccess}
                                    disabled={fetchingDatasets || submitFormIssues.length > 0}
                                >
                                    {t('Submit access requests')}
                                </Button>
                            </Flex>
                        </Form.Item>
                    </Form>
                    <Divider />
                    <Flex vertical>
                        <Typography.Text>
                            <CheckCircleOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('Owners typically respond within 24-48 hours')}
                        </Typography.Text>
                        <Typography.Text>
                            <BellOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('You will get notified when access is granted or denied')}
                        </Typography.Text>
                        <Typography.Text>
                            <MessageOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('Message owners directly for questions')}
                        </Typography.Text>
                    </Flex>
                </Card>
            </Col>
        </Row>
    );
}
