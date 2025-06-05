import { Button, Col, Form, type FormProps, Input, Popconfirm, Row, Select, Space } from 'antd';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';

import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetAllDataProductLifecyclesQuery } from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import { useGetAllDataProductTypesQuery } from '@/store/features/data-product-types/data-product-types-api-slice.ts';
import {
    useCreateDataProductMutation,
    useGetDataProductByIdQuery,
    useGetDataProductNamespaceLengthLimitsQuery,
    useLazyGetDataProductNamespaceSuggestionQuery,
    useLazyValidateDataProductNamespaceQuery,
    useRemoveDataProductMutation,
    useUpdateDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetAllDomainsQuery } from '@/store/features/domains/domains-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
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
    const navigate = useNavigate();

    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId || '',
        { skip: mode === 'create' || !dataProductId },
    );
    const { data: lifecycles = [], isFetching: isFetchingLifecycles } = useGetAllDataProductLifecyclesQuery();
    const { data: domains = [], isFetching: isFetchingDomains } = useGetAllDomainsQuery();
    const { data: dataProductTypes = [], isFetching: isFetchingDataProductTypes } = useGetAllDataProductTypesQuery();
    const { data: dataProductOwners = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const { data: availableTags = [], isFetching: isFetchingTags } = useGetAllTagsQuery();
    const [createDataProduct, { isLoading: isCreating }] = useCreateDataProductMutation();
    const [updateDataProduct, { isLoading: isUpdating }] = useUpdateDataProductMutation();
    const [deleteDataProduct, { isLoading: isArchiving }] = useRemoveDataProductMutation();
    const [fetchNamespace, { data: namespaceSuggestion }] = useLazyGetDataProductNamespaceSuggestionQuery();

    const ownerIds = useGetDataProductOwnerIds(currentDataProduct?.id);
    const [validateNamespace] = useLazyValidateDataProductNamespaceQuery();
    const { data: namespaceLengthLimits } = useGetDataProductNamespaceLengthLimitsQuery();

    const [form] = Form.useForm<DataProductCreateFormSchema>();
    const dataProductNameValue = Form.useWatch('name', form);

    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);

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

    const dataProductTypeSelectOptions = dataProductTypes.map((type) => ({ label: type.name, value: type.id }));
    const domainSelectOptions = domains.map((domain) => ({ label: domain.name, value: domain.id }));
    const userSelectOptions = dataProductOwners.map((owner) => ({ label: owner.email, value: owner.id }));
    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id }));

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
                dispatchMessage({ content: t('Data product created successfully'), type: 'success' });

                navigate(createDataProductIdPath(response.id));
            } else if (mode === 'edit' && dataProductId) {
                if (!canEdit) {
                    dispatchMessage({ content: t('You are not allowed to edit this data product'), type: 'error' });
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

                dispatchMessage({ content: t('Data product updated successfully'), type: 'success' });
                navigate(createDataProductIdPath(response.id));
            }

            form.resetFields();
        } catch (_e) {
            const errorMessage =
                mode === 'edit' ? t('Failed to update data product') : t('Failed to create data product');
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
                dispatchMessage({ content: t('Data product deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.DataProducts);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete data product, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    const fetchNamespaceDebounced = useDebouncedCallback((name: string) => fetchNamespace(name), DEBOUNCE);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFields([
                {
                    name: 'namespace',
                    validating: true,
                    errors: [],
                },
            ]);
            fetchNamespaceDebounced(dataProductNameValue ?? '');
        }
    }, [mode, form, canEditNamespace, dataProductNameValue, fetchNamespaceDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFieldValue('namespace', namespaceSuggestion?.namespace);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditNamespace, namespaceSuggestion]);

    useEffect(() => {
        if (currentDataProduct && mode === 'edit') {
            console.log(ownerIds);
            form.setFieldsValue({
                namespace: currentDataProduct.namespace,
                name: currentDataProduct.name,
                description: currentDataProduct.description,
                type_id: currentDataProduct.type.id,
                lifecycle_id: currentDataProduct.lifecycle.id,
                domain_id: currentDataProduct.domain.id,
                tag_ids: currentDataProduct.tags.map((tag) => tag.id),
                owners: ownerIds,
            });
        }
    }, [currentDataProduct, form, mode, ownerIds]);

    const validateNamespaceCallback = useCallback(
        (namespace: string) => validateNamespace(namespace).unwrap(),
        [validateNamespace],
    );

    return (
        <Form<DataProductCreateFormSchema>
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            labelWrap
            disabled={isLoading || !canSubmit}
        >
            <Form.Item<DataProductCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your data product')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the data product'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <NamespaceFormItem
                form={form}
                tooltip={t('The namespace of the data product')}
                max_length={namespaceLengthLimits?.max_length}
                editToggleDisabled={mode === 'edit'}
                canEditNamespace={canEditNamespace}
                toggleCanEditNamespace={() => setCanEditNamespace((prev) => !prev)}
                validationRequired={mode === 'create'}
                validateNamespace={validateNamespaceCallback}
            />
            <Form.Item<DataProductCreateFormSchema>
                name={'owners'}
                label={t('Owners')}
                tooltip={t('The owners of the data product')}
                rules={[
                    {
                        required: true,
                        message: t('Please select at least one owner for the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingUsers}
                    mode={'multiple'}
                    options={userSelectOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                    disabled={mode !== 'create'}
                    tokenSeparators={[',']}
                    allowClear
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'type_id'}
                label={t('Type')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the type of the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDataProductTypes}
                    allowClear
                    showSearch
                    options={dataProductTypeSelectOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'lifecycle_id'}
                label={t('Status')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the status of the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingLifecycles}
                    allowClear
                    showSearch
                    options={lifecycles.map((lifecycle) => ({ value: lifecycle.id, label: lifecycle.name }))}
                    filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'domain_id'}
                label={t('Domain')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the domain of the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDomains}
                    options={domainSelectOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                    allowClear
                    showSearch
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select data product tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    filterOption={selectFilterOptionByLabel}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the data product')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the data product'),
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
                                title={t('Are you sure you want to delete this data product?')}
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
