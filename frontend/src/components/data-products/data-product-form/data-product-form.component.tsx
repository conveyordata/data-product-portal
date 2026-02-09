import { usePostHog } from '@posthog/react';
import { Button, Col, Form, type FormProps, Input, Popconfirm, Row, Select, Skeleton, Space } from 'antd';
import { parseAsBoolean, useQueryState } from 'nuqs';
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetDataProductsLifecyclesQuery } from '@/store/api/services/generated/configurationDataProductLifecyclesApi.ts';
import { useGetDataProductsTypesQuery } from '@/store/api/services/generated/configurationDataProductTypesApi.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import { useGetTagsQuery } from '@/store/api/services/generated/configurationTagsApi.ts';
import {
    ResourceNameModel,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
    useResourceNameConstraintsQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useCreateDataProductMutation,
    useGetDataProductByIdQuery,
    useRemoveDataProductMutation,
    useUpdateDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataProductCreate, DataProductCreateFormSchema, DataProductUpdateRequest } from '@/types/data-product';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { useGetDataProductOwnerIds } from '@/utils/data-product-user-role.helper.ts';
import { selectFilterOptionByLabel, selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';
import styles from './data-product-form.module.scss';

const { TextArea } = Input;

const DEBOUNCE = 500;

type Props = {
    mode: 'create' | 'edit';
    dataProductId?: string;
};

export function DataProductForm({ mode, dataProductId }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);
    const [fromMarketplace] = useQueryState('fromMarketplace', parseAsBoolean.withDefault(false));

    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId || '',
        { skip: mode === 'create' || !dataProductId },
    );
    const { data: lifecycles = undefined, isFetching: isFetchingLifecycles } = useGetDataProductsLifecyclesQuery();
    const { data: { domains = [] } = {}, isFetching: isFetchingDomains } = useGetDomainsQuery();
    const { data: dataProductTypes = undefined, isFetching: isFetchingDataProductTypes } =
        useGetDataProductsTypesQuery();
    const { data: { users: dataProductOwners = [] } = {}, isFetching: isFetchingUsers } = useGetUsersQuery();
    const { data: { tags: availableTags = [] } = {}, isFetching: isFetchingTags } = useGetTagsQuery();
    const [createDataProduct, { isLoading: isCreating }] = useCreateDataProductMutation();
    const [updateDataProduct, { isLoading: isUpdating }] = useUpdateDataProductMutation();
    const [deleteDataProduct, { isLoading: isArchiving }] = useRemoveDataProductMutation();
    const [sanitizeResourceName, { data: sanitizedResourceName }] = useLazySanitizeResourceNameQuery();
    const [validateResourceName] = useLazyValidateResourceNameQuery();
    const { data: constraints } = useResourceNameConstraintsQuery();

    const [form] = Form.useForm<DataProductCreateFormSchema>();
    const dataProductNameValue = Form.useWatch('name', form);

    const [canEditResourceName, setCanEditResourceName] = useState<boolean>(false);

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

    const isLoading =
        isCreating ||
        isUpdating ||
        isCreating ||
        isUpdating ||
        isFetchingInitialValues ||
        isFetchingTags ||
        isFetchingLifecycles;

    const dataProductTypeSelectOptions = dataProductTypes?.data_product_types.map((type) => ({
        label: type.name,
        value: type.id,
    }));
    const domainSelectOptions = domains.map((domain) => ({ label: domain.name, value: domain.id }));
    const userSelectOptions = dataProductOwners.map((owner) => ({
        label: `${owner.first_name} ${owner.last_name} (${owner.email})`,
        value: owner.id,
        disabled: owner.id === currentUser?.id,
    }));
    const tagSelectOptions = availableTags.map((tag) => ({ label: tag.value, value: tag.id }));

    const onFinish: FormProps<DataProductCreateFormSchema>['onFinish'] = async (values) => {
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
                dispatchMessage({ content: t('Data Product created successfully'), type: 'success' });
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
                    dispatchMessage({ content: t('You are not allowed to edit this Data Product'), type: 'error' });
                    return;
                }

                const request: DataProductUpdateRequest = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    type_id: values.type_id,
                    lifecycle_id: values.lifecycle_id,
                    domain_id: values.domain_id,
                    tag_ids: values.tag_ids,
                };
                const response = await updateDataProduct({
                    dataProduct: request,
                    data_product_id: dataProductId,
                }).unwrap();

                dispatchMessage({ content: t('Data Product updated successfully'), type: 'success' });
                navigate(createDataProductIdPath(response.id));
            }

            form.resetFields();
        } catch (_e) {
            const errorMessage =
                mode === 'edit' ? t('Failed to update Data Product') : t('Failed to create Data Product');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && dataProductId) {
            navigate(createDataProductIdPath(dataProductId));
        } else {
            navigate(ApplicationPaths.DataProducts);
        }
    };

    const onFinishFailed: FormProps<DataProductCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const handleDeleteDataProduct = async () => {
        if (canDelete && currentDataProduct) {
            try {
                await deleteDataProduct(currentDataProduct?.id).unwrap();
                dispatchMessage({ content: t('Data Product deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.DataProducts);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete Data Product, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    const fetchResourceNameDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), DEBOUNCE);

    useEffect(() => {
        if (mode === 'create' && !canEditResourceName) {
            form.setFields([
                {
                    name: 'namespace',
                    validating: true,
                    errors: [],
                },
            ]);
            fetchResourceNameDebounced(dataProductNameValue ?? '');
        }
    }, [form, mode, canEditResourceName, dataProductNameValue, fetchResourceNameDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditResourceName) {
            form.setFieldValue('namespace', sanitizedResourceName?.resource_name);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditResourceName, sanitizedResourceName]);

    const resourceNameValidationCallback = useCallback(
        (resourceName: string) =>
            validateResourceName({ resourceName: resourceName, model: ResourceNameModel.DataProduct }).unwrap(),
        [validateResourceName],
    );

    const ownerIds = useGetDataProductOwnerIds(currentDataProduct?.id);

    if (mode === 'edit' && (!currentDataProduct || ownerIds === undefined)) {
        return <Skeleton active />;
    }

    const initialValues = {
        name: currentDataProduct?.name,
        namespace: currentDataProduct?.namespace,
        description: currentDataProduct?.description,
        type_id: currentDataProduct?.type.id,
        lifecycle_id: currentDataProduct?.lifecycle.id,
        domain_id: currentDataProduct?.domain.id,
        tag_ids: currentDataProduct?.tags.map((tag) => tag.id),
        owners: mode === 'edit' ? ownerIds : currentUser?.id ? [currentUser?.id] : [],
    };

    return (
        <Form<DataProductCreateFormSchema>
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
            <Form.Item<DataProductCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Data Product'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <ResourceNameFormItem
                form={form}
                tooltip={t('The namespace of the Data Product')}
                max_length={constraints?.max_length}
                editToggleDisabled={mode === 'edit'}
                canEditResourceName={canEditResourceName}
                toggleCanEditResourceName={() => setCanEditResourceName((prev) => !prev)}
                validationRequired={mode === 'create'}
                validateResourceName={resourceNameValidationCallback}
            />
            <Form.Item<DataProductCreateFormSchema>
                name={'owners'}
                label={t('Owners')}
                tooltip={t('The owners of the Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please select at least one owner for the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingUsers}
                    mode={'multiple'}
                    options={userSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    disabled={mode !== 'create'}
                    tokenSeparators={[',']}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'type_id'}
                label={t('Type')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the type of the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDataProductTypes}
                    allowClear
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    options={dataProductTypeSelectOptions}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'lifecycle_id'}
                label={t('Status')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the status of the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingLifecycles}
                    options={lifecycles?.data_product_life_cycles.map((lifecycle) => ({
                        value: lifecycle.id,
                        label: lifecycle.name,
                    }))}
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    allowClear
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'domain_id'}
                label={t('Domain')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the domain of the Data Product'),
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
            <Form.Item<DataProductCreateFormSchema> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select Data Product tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabel }}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Data Product'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than 255 characters'),
                    },
                ]}
            >
                <TextArea rows={4} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item>
                <Row>
                    {mode !== 'create' && (
                        <Col>
                            <Popconfirm
                                title={t('Are you sure you want to delete this Data Product?')}
                                onConfirm={handleDeleteDataProduct}
                                okText={t('Yes')}
                                cancelText={t('No')}
                            >
                                <Button
                                    className={styles.formButton}
                                    type="default"
                                    danger
                                    loading={isArchiving}
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
    );
}
