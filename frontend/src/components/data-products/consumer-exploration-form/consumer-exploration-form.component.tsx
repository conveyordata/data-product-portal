import { ProductOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Button, Col, Form, type FormProps, Input, Popconfirm, Row, Select, Skeleton, Space, Typography } from 'antd';
import { parseAsBoolean, useQueryState } from 'nuqs';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import { useGetTagsQuery } from '@/store/api/services/generated/configurationTagsApi.ts';
import {
    type DataProductCreate,
    type DataProductUpdate,
    useCreateDataProductMutation,
    useGetDataProductQuery,
    useRemoveDataProductMutation,
    useUpdateDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { useGetDataProductOwnerIds } from '@/utils/data-product-user-role.helper.ts';
import { selectFilterOptionByLabel, selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';
import styles from './consumer-exploration-form.module.scss';

type Props = {
    mode: 'create' | 'edit';
    dataProductId?: string;
    debounce?: number;
};

export function ConsumerExplorationForm({ mode, dataProductId }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);
    const [fromMarketplace] = useQueryState('fromMarketplace', parseAsBoolean.withDefault(false));

    const [deleteDataProduct, { isLoading: isDeleting, isSuccess: isDeleted }] = useRemoveDataProductMutation();
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductQuery(
        dataProductId || '',
        { skip: mode === 'create' || !dataProductId || isDeleted || isDeleting },
    );
    const { data: { domains = [] } = {}, isFetching: isFetchingDomains } = useGetDomainsQuery();
    const { data: { users: dataProductOwners = [] } = {}, isFetching: isFetchingUsers } = useGetUsersQuery();
    const { data: { tags: availableTags = [] } = {}, isFetching: isFetchingTags } = useGetTagsQuery();
    const [createDataProduct, { isLoading: isCreating }] = useCreateDataProductMutation();
    const [updateDataProduct, { isLoading: isUpdating }] = useUpdateDataProductMutation();

    const [form] = Form.useForm<DataProductCreate>();

    const { data: create_access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT });
    const { data: update_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );
    const { data: delete_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__DELETE,
        },
        { skip: !dataProductId },
    );

    const canCreate = mode === 'create' && (create_access?.allowed ?? false);
    const canEdit = mode === 'edit' && (update_access?.allowed ?? false);
    const canDelete = mode === 'edit' && (delete_access?.allowed ?? false);
    const canSubmit = canCreate || canEdit;

    const isLoading = isCreating || isUpdating || isCreating || isUpdating || isFetchingInitialValues || isFetchingTags;

    const domainSelectOptions = domains.map((domain) => ({ label: domain.name, value: domain.id }));
    const userSelectOptions = dataProductOwners.map((owner) => ({
        label: `${owner.first_name} ${owner.last_name} (${owner.email})`,
        value: owner.id,
        disabled: owner.id === currentUser?.id,
    }));
    const tagSelectOptions = availableTags.map((tag) => ({ label: tag.value, value: tag.id }));

    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        if (mode === 'edit') {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            <ProductOutlined /> {t('Product Studio')}
                        </>
                    ),
                    path: ApplicationPaths.Studio,
                },
                { title: <>{currentDataProduct?.name}</>, path: createDataProductIdPath(dataProductId ?? '') },
                { title: t('Edit') },
            ]);
        }
        if (mode === 'create') {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            <ProductOutlined /> {t('Product Studio')}
                        </>
                    ),
                    path: ApplicationPaths.Studio,
                },
                { title: t('New Consumer Exploration') },
            ]);
        }
    }, [setBreadcrumbs, t, dataProductId, mode, currentDataProduct?.name]);

    const onFinish: FormProps<DataProductCreate>['onFinish'] = async (values) => {
        try {
            if (mode === 'create') {
                const request: DataProductCreate = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    owners: values.owners,
                    lifecycle_id: values.lifecycle_id,
                    type_id: values.type_id,
                    tag_ids: values.tag_ids ?? [],
                    domain_id: values.domain_id,
                };
                const response = await createDataProduct(request).unwrap();
                dispatchMessage({ content: t('Consumer Exploration created successfully'), type: 'success' });
                posthog.capture(PosthogEvents.CREATE_DATA_PRODUCT_COMPLETED);

                if (fromMarketplace) {
                    navigate({
                        pathname: ApplicationPaths.MarketplaceCart,
                        search: new URLSearchParams({ createdProductId: response.id }).toString(),
                    });
                } else {
                    navigate(createDataProductIdPath(response.id));
                }
            } else if (mode === 'edit' && dataProductId) {
                if (!canEdit) {
                    dispatchMessage({
                        content: t('You are not allowed to edit this Consumer Exploration'),
                        type: 'error',
                    });
                    return;
                }

                const request: DataProductUpdate = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    type_id: values.type_id,
                    lifecycle_id: values.lifecycle_id,
                    domain_id: values.domain_id,
                    tag_ids: values.tag_ids,
                };
                const response = await updateDataProduct({
                    dataProductUpdate: request,
                    id: dataProductId,
                }).unwrap();

                dispatchMessage({ content: t('Consumer Exploration updated successfully'), type: 'success' });
                navigate(createDataProductIdPath(response.id));
            }

            form.resetFields();
        } catch (_e) {
            const errorMessage =
                mode === 'edit'
                    ? t('Failed to update Consumer Exploration')
                    : t('Failed to create Consumer Exploration');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && dataProductId) {
            navigate(createDataProductIdPath(dataProductId));
        } else {
            navigate(ApplicationPaths.Studio);
        }
    };

    const onFinishFailed: FormProps<DataProductCreate>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const handleDeleteDataProduct = async () => {
        if (canDelete && currentDataProduct) {
            try {
                await deleteDataProduct(currentDataProduct?.id).unwrap();
                dispatchMessage({ content: t('Consumer Exploration deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.Studio);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete Consumer Exploration, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    const ownerIds = useGetDataProductOwnerIds(currentDataProduct?.id);

    if (mode === 'edit' && (!currentDataProduct || ownerIds === undefined)) {
        return <Skeleton active />;
    }

    const initialValues = {
        name: currentDataProduct?.name,
        type_id: currentDataProduct?.type.id,
        lifecycle_id: currentDataProduct?.lifecycle?.id,
        domain_id: currentDataProduct?.domain.id,
        tag_ids: currentDataProduct?.tags.map((tag) => tag.id),
        owners: mode === 'edit' ? ownerIds : currentUser?.id ? [currentUser?.id] : [],
    };

    return (
        <>
            {mode === 'edit' && (
                <Typography.Title level={3} className={styles.title}>
                    {currentDataProduct?.name}
                </Typography.Title>
            )}
            {mode === 'create' && <Typography.Title level={3}>{t('New Consumer Exploration')}</Typography.Title>}
            <Form<DataProductCreate>
                form={form}
                labelWrap
                labelCol={FORM_GRID_WRAPPER_COLS}
                wrapperCol={FORM_GRID_WRAPPER_COLS}
                layout="vertical"
                onFinish={onFinish}
                onFinishFailed={onFinishFailed}
                autoComplete={'off'}
                requiredMark={'optional'}
                disabled={isLoading || !canSubmit}
                initialValues={initialValues}
            >
                <Form.Item<DataProductCreate>
                    name={'name'}
                    label={t('Name')}
                    tooltip={t('The name of your Consumer Exploration')}
                    rules={[
                        {
                            required: true,
                            message: t('Please provide the name of the Consumer Exploration'),
                        },
                    ]}
                >
                    <Input />
                </Form.Item>
                <Form.Item<DataProductCreate>
                    name={'owners'}
                    label={t('Owners')}
                    tooltip={t('The owners of the Consumer Exploration')}
                    rules={[
                        {
                            required: true,
                            message: t('Please select at least one owner for the Consumer Exploration'),
                        },
                    ]}
                >
                    <Select
                        loading={isFetchingUsers}
                        mode="multiple"
                        options={userSelectOptions}
                        showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                        disabled={mode !== 'create'}
                        tokenSeparators={[',']}
                    />
                </Form.Item>
                <Form.Item<DataProductCreate>
                    name={'domain_id'}
                    label={t('Domain')}
                    rules={[
                        {
                            required: true,
                            message: t('Please select the domain of the Consumer Exploration'),
                        },
                    ]}
                >
                    <Select
                        loading={isFetchingDomains}
                        options={domainSelectOptions}
                        showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                        allowClear
                    />
                </Form.Item>
                <Form.Item<DataProductCreate> name={'tag_ids'} label={t('Tags')}>
                    <Select
                        tokenSeparators={[',']}
                        placeholder={t('Select Consumer Exploration tags')}
                        mode={'multiple'}
                        options={tagSelectOptions}
                        showSearch={{ filterOption: selectFilterOptionByLabel }}
                    />
                </Form.Item>
                <Form.Item>
                    <Row>
                        {mode !== 'create' && (
                            <Col>
                                <Popconfirm
                                    title={t('Are you sure you want to delete this Consumer Exploration?')}
                                    onConfirm={handleDeleteDataProduct}
                                    okText={t('Yes')}
                                    cancelText={t('No')}
                                >
                                    <Button
                                        className={styles.formButton}
                                        type="default"
                                        danger
                                        loading={isDeleting}
                                        disabled={isLoading || !canDelete}
                                    >
                                        {t('Delete')}
                                    </Button>
                                </Popconfirm>
                            </Col>
                        )}
                        <Col flex="auto" />
                        <Col>
                            <Space>
                                <Button
                                    className={styles.formButton}
                                    type="default"
                                    onClick={onCancel}
                                    loading={isCreating || isUpdating}
                                    disabled={isLoading}
                                >
                                    {t('Cancel')}
                                </Button>
                                <Button
                                    className={styles.formButton}
                                    type="primary"
                                    htmlType={'submit'}
                                    loading={isCreating || isUpdating}
                                    disabled={isLoading || !canSubmit}
                                >
                                    {mode === 'edit' ? t('Save') : t('Create')}
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Form.Item>
            </Form>
        </>
    );
}
