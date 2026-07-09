import { ProductOutlined } from '@ant-design/icons';
import { Button, Col, Form, Popconfirm, Row, Skeleton, Space, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import styles from '@/components/data-products/data-product-form/data-product-form.module.scss';
import { ExplorationFormItems } from '@/components/explorations/exploration-form/exploration-form-items.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    type Exploration,
    useGetExplorationQuery,
    useRemoveExplorationMutation,
} from '@/store/api/services/generated/explorationsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { ApplicationPaths, createExplorationIdPath } from '@/types/navigation.ts';

type Props = {
    explorationId?: string;
};

export function ExplorationForm({ explorationId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);

    const [deleteExploration, { isLoading: isDeleting, isSuccess: isDeleted }] = useRemoveExplorationMutation();
    const { data: currentExploration, isLoading } = useGetExplorationQuery(explorationId ?? '', {
        skip: !explorationId || isDeleted || isDeleting,
    });

    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined /> {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: currentExploration?.name, path: createExplorationIdPath(currentExploration?.id ?? '') },
            { title: t('Edit') },
        ]);
    }, [t, setBreadcrumbs, currentExploration]);

    const canDelete = currentExploration?.owner.id === currentUser?.id;

    const [form] = Form.useForm<Exploration>();

    const onCancel = () => {
        form.resetFields();
        if (explorationId) {
            navigate(createExplorationIdPath(explorationId));
        } else {
            navigate(ApplicationPaths.Studio);
        }
    };

    const handleDeleteExploration = async () => {
        if (currentExploration) {
            try {
                await deleteExploration(currentExploration.id).unwrap();
                dispatchMessage({ content: t('Exploration deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.Studio);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete Exploration, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    if (!currentExploration) {
        return <Skeleton active />;
    }

    const initialValues = {
        name: currentExploration.name,
        namespace: currentExploration.namespace,
        domain: currentExploration.domain.id,
        description: currentExploration.description,
    };

    return (
        <>
            <Typography.Title level={3} className={styles.title}>
                {currentExploration.name}
            </Typography.Title>
            <Form<Exploration>
                form={form}
                labelWrap
                labelCol={FORM_GRID_WRAPPER_COLS}
                wrapperCol={FORM_GRID_WRAPPER_COLS}
                layout="vertical"
                autoComplete="off"
                disabled={true}
                initialValues={initialValues}
            >
                <ExplorationFormItems />
                <Form.Item>
                    <Row>
                        <Col>
                            <Popconfirm
                                title={t('Are you sure you want to delete this Exploration?')}
                                onConfirm={handleDeleteExploration}
                                okText={t('Yes')}
                                okButtonProps={{ disabled: false }}
                                showCancel={false}
                            >
                                <Button
                                    className={styles.formButton}
                                    type="default"
                                    danger
                                    loading={isDeleting}
                                    disabled={!canDelete}
                                >
                                    {t('Delete')}
                                </Button>
                            </Popconfirm>
                        </Col>
                        <Col flex="auto" />
                        <Col>
                            <Space>
                                <Button
                                    className={styles.formButton}
                                    type="default"
                                    onClick={onCancel}
                                    loading={isDeleting}
                                    disabled={isLoading}
                                >
                                    {t('Cancel')}
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Form.Item>
            </Form>
        </>
    );
}
