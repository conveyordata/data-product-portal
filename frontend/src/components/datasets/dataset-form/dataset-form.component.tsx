import {
    Button,
    type CheckboxOptionType,
    Col,
    Form,
    type FormInstance,
    type FormProps,
    Input,
    Popconfirm,
    Radio,
    Row,
    Select,
    Skeleton,
    Space,
    Tooltip,
} from 'antd';
import type { TFunction } from 'i18next';
import { type Ref, useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';

import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { useGetDataProductsLifecyclesQuery } from '@/store/api/services/generated/configurationDataProductLifecyclesApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRequestDatasetAccessForDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import {
    useCreateDatasetMutation,
    useGetDatasetByIdQuery,
    useGetDatasetNamespaceLengthLimitsQuery,
    useLazyGetDatasetNamespaceSuggestionQuery,
    useLazyValidateDatasetNamespaceQuery,
    useRemoveDatasetMutation,
    useUpdateDatasetMutation,
} from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import {
    DatasetAccess,
    type DatasetCreateFormSchema,
    type DatasetCreateRequest,
    type DatasetUpdateRequest,
} from '@/types/dataset';
import {
    ApplicationPaths,
    createDataOutputIdPath,
    createDataProductIdPath,
    createDatasetIdPath,
} from '@/types/navigation.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';
import { useGetDataProductOwnerIds } from '@/utils/data-product-user-role.helper';
import { useGetDatasetOwnerIds } from '@/utils/dataset-user-role.helper.ts';
import { selectFilterOptionByLabel, selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';
import styles from './dataset-form.module.scss';

type Props = {
    mode: 'create' | 'edit';
    datasetId?: string;
    dataProductId?: string;
    dataOutputId?: string;
    modalCallbackOnSubmit?: () => void;
    formRef?: Ref<FormInstance<DatasetCreateFormSchema>>;
};

const { TextArea } = Input;

const DEBOUNCE = 500;

const getAccessTypeOptions = (t: TFunction) => {
    return [
        {
            label: (
                <Tooltip title={t('Public output ports are visible to everyone and are free to use by anyone')}>
                    {getDatasetAccessTypeLabel(t, DatasetAccess.Public)}
                </Tooltip>
            ),
            value: DatasetAccess.Public,
        },
        {
            label: (
                <Tooltip title={t('Restricted output ports are visible to everyone but require permission to use')}>
                    {getDatasetAccessTypeLabel(t, DatasetAccess.Restricted)}
                </Tooltip>
            ),
            value: DatasetAccess.Restricted,
        },
        {
            label: (
                <Tooltip title={t('Private output ports are only visible to owners and users with access')}>
                    {getDatasetAccessTypeLabel(t, DatasetAccess.Private)}
                </Tooltip>
            ),
            value: DatasetAccess.Private,
        },
    ];
};

export function DatasetForm({ mode, modalCallbackOnSubmit, formRef, datasetId, dataProductId, dataOutputId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: currentDataset, isFetching: isFetchingInitialValues } = useGetDatasetByIdQuery(datasetId || '', {
        skip: mode === 'create' || !datasetId,
    });
    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductByIdQuery(dataProductId || '', {
        skip: mode === 'edit' || !dataProductId,
    });
    const { data: lifecycles = undefined, isFetching: isFetchingLifecycles } = useGetDataProductsLifecyclesQuery();
    const { data: users = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const [createDataset, { isLoading: isCreating }] = useCreateDatasetMutation();
    const [requestDatasetsAccessForDataOutput] = useRequestDatasetAccessForDataOutputMutation();
    const [updateDataset, { isLoading: isUpdating }] = useUpdateDatasetMutation();
    const [deleteDataset, { isLoading: isArchiving }] = useRemoveDatasetMutation();
    const [fetchNamespace, { data: namespaceSuggestion }] = useLazyGetDatasetNamespaceSuggestionQuery();
    const [validateNamespace] = useLazyValidateDatasetNamespaceQuery();
    const { data: namespaceLengthLimits } = useGetDatasetNamespaceLengthLimitsQuery();

    const [form] = Form.useForm<DatasetCreateFormSchema>();
    const datasetNameValue = Form.useWatch('name', form);

    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);

    const { data: create_access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATASET });
    const { data: update_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const { data: delete_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__DELETE,
        },
        { skip: !datasetId },
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
        isFetchingDataProduct ||
        isFetchingInitialValues ||
        isFetchingTags;

    const accessTypeOptions: CheckboxOptionType<DatasetAccess>[] = useMemo(() => getAccessTypeOptions(t), [t]);

    const userSelectOptions = users.map((owner) => ({
        label: `${owner.first_name} ${owner.last_name} (${owner.email})`,
        value: owner.id,
    }));
    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];

    const onFinish: FormProps<DatasetCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (mode === 'create' && dataProduct) {
                const request: DatasetCreateRequest = {
                    name: values.name,
                    namespace: values.namespace,
                    data_product_id: dataProduct.id,
                    description: values.description,
                    owners: values.owners,
                    tag_ids: values.tag_ids ?? [],
                    domain_id: dataProduct.domain.id,
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };
                const response = await createDataset(request).unwrap();

                modalCallbackOnSubmit?.();
                dispatchMessage({ content: t('Output port created successfully'), type: 'success' });
                // If dataProductId was provided, navigate back to the data product page
                if (dataOutputId && dataProductId) {
                    await requestDatasetsAccessForDataOutput({
                        dataOutputId: dataOutputId,
                        datasetId: response.id,
                    });
                    navigate(createDataOutputIdPath(dataOutputId, dataProductId));
                } else {
                    if (dataProductId) {
                        navigate(createDataProductIdPath(dataProductId, TabKeys.OutputPorts));
                    } else {
                        navigate(createDatasetIdPath(response.id));
                    }
                }
            } else if (mode === 'edit' && datasetId && currentDataset) {
                if (!canEdit) {
                    dispatchMessage({ content: t('You are not allowed to edit this output port'), type: 'error' });
                    return;
                }

                const request: DatasetUpdateRequest = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    data_product_id: currentDataset.data_product_id,
                    tag_ids: values.tag_ids,
                    domain_id: currentDataset.domain.id,
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };

                const response = await updateDataset({ dataset: request, id: datasetId }).unwrap();
                dispatchMessage({ content: t('Output port updated successfully'), type: 'success' });

                navigate(createDatasetIdPath(response.id));
            }
            form.resetFields();
        } catch (_e) {
            const errorMessage =
                mode === 'edit' ? t('Failed to update output port') : t('Failed to create output port');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && datasetId) {
            navigate(createDatasetIdPath(datasetId));
        } else if (dataOutputId && dataProductId) {
            navigate(createDataOutputIdPath(dataOutputId, dataProductId));
        } else {
            navigate(ApplicationPaths.Datasets);
        }
    };

    const onFinishFailed: FormProps<DatasetCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const handleDeleteDataset = async () => {
        if (canDelete && currentDataset) {
            try {
                await deleteDataset(currentDataset);
                dispatchMessage({ content: t('Output port deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.Datasets);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete output port, please try again later'),
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
            fetchNamespaceDebounced(datasetNameValue ?? '');
        }
    }, [mode, form, canEditNamespace, datasetNameValue, fetchNamespaceDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFieldValue('namespace', namespaceSuggestion?.namespace);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditNamespace, namespaceSuggestion]);

    const validateNamespaceCallback = useCallback(
        (namespace: string) => validateNamespace(namespace).unwrap(),
        [validateNamespace],
    );
    const datasetOwners = useGetDatasetOwnerIds(currentDataset?.id);
    const dataProductOwners = useGetDataProductOwnerIds(dataProduct?.id);
    const ownerIds = mode === 'edit' ? datasetOwners : dataProductOwners;

    if (mode === 'edit' && (!currentDataset || ownerIds === undefined)) {
        return <Skeleton active />;
    }

    const initialValues = {
        name: currentDataset?.name,
        namespace: currentDataset?.namespace,
        description: currentDataset?.description,
        access_type: mode === 'create' ? DatasetAccess.Public : currentDataset?.access_type,
        lifecycle_id: currentDataset?.lifecycle.id,
        tag_ids: currentDataset?.tags.map((tag) => tag.id),
        owners: ownerIds,
    };

    return (
        <Form<DatasetCreateFormSchema>
            form={form}
            ref={formRef}
            labelWrap
            labelCol={mode === 'edit' ? FORM_GRID_WRAPPER_COLS : undefined}
            wrapperCol={mode === 'edit' ? FORM_GRID_WRAPPER_COLS : undefined}
            layout="vertical"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            disabled={isLoading || !canSubmit}
            initialValues={initialValues}
        >
            <Form.Item<DatasetCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your output port')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the output port'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <NamespaceFormItem
                form={form}
                tooltip={t('The namespace of the output port')}
                max_length={namespaceLengthLimits?.max_length}
                editToggleDisabled={mode === 'edit'}
                canEditNamespace={canEditNamespace}
                toggleCanEditNamespace={() => setCanEditNamespace((prev) => !prev)}
                validationRequired={mode === 'create'}
                validateNamespace={validateNamespaceCallback}
            />
            {mode === 'create' && (
                <Form.Item<DatasetCreateFormSchema>
                    name={'owners'}
                    label={t('Owners')}
                    tooltip={t('The owners of the output port')}
                    rules={[
                        {
                            required: true,
                            message: t('Please select at least one owner for the output port'),
                        },
                    ]}
                >
                    <Select
                        loading={isFetchingUsers}
                        mode={'multiple'}
                        options={userSelectOptions}
                        showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                        tokenSeparators={[',']}
                        allowClear
                    />
                </Form.Item>
            )}
            <Form.Item<DatasetCreateFormSchema>
                name={'lifecycle_id'}
                label={t('Status')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the status of the output port'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingLifecycles}
                    allowClear
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    options={lifecycles?.data_product_life_cycles.map((lifecycle) => ({
                        value: lifecycle.id,
                        label: lifecycle.name,
                    }))}
                />
            </Form.Item>
            <Form.Item<DatasetCreateFormSchema>
                name={'access_type'}
                label={t('Access Type')}
                tooltip={t('The access type of the output port')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the access type of the output port'),
                    },
                ]}
            >
                <Radio.Group options={accessTypeOptions} />
            </Form.Item>
            <Form.Item<DatasetCreateFormSchema> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select output port tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabel }}
                />
            </Form.Item>
            <Form.Item<DatasetCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the output port')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the output port'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than 255 characters'),
                    },
                ]}
            >
                <TextArea rows={4} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            {mode !== 'create' && (
                <Form.Item>
                    <Row>
                        <Col>
                            <Popconfirm
                                title={t('Are you sure you want to delete this output port?')}
                                onConfirm={handleDeleteDataset}
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
                                    {t('Save')}
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Form.Item>
            )}
        </Form>
    );
}
