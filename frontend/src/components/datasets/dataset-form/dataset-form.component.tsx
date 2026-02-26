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
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDataProductsLifecyclesQuery } from '@/store/api/services/generated/configurationDataProductLifecyclesApi.ts';
import { useGetTagsQuery } from '@/store/api/services/generated/configurationTagsApi.ts';
import { OutputPortAccessType, useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    type CreateOutputPortRequest,
    type DatasetUpdate,
    useCreateOutputPortMutation,
    useGetOutputPortQuery,
    useRemoveOutputPortMutation,
    useUpdateOutputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useLinkOutputPortToTechnicalAssetMutation } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import {
    ResourceNameModel,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
    useResourceNameConstraintsQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { DatasetAccess } from '@/types/dataset';
import {
    ApplicationPaths,
    createDataOutputIdPath,
    createDataProductIdPath,
    createMarketplaceOutputPortPath,
    createOutputPortPath,
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
    formRef?: Ref<FormInstance<CreateOutputPortRequest>>;
};

const { TextArea } = Input;

const DEBOUNCE = 500;

const getAccessTypeOptions = (t: TFunction) => {
    return [
        {
            label: (
                <Tooltip title={t('Public Output Ports are visible to everyone and are free to use by anyone')}>
                    {getDatasetAccessTypeLabel(t, OutputPortAccessType.Public)}
                </Tooltip>
            ),
            value: DatasetAccess.Public,
        },
        {
            label: (
                <Tooltip title={t('Restricted Output Ports are visible to everyone but require permission to use')}>
                    {getDatasetAccessTypeLabel(t, OutputPortAccessType.Restricted)}
                </Tooltip>
            ),
            value: DatasetAccess.Restricted,
        },
        {
            label: (
                <Tooltip title={t('Private Output Ports are only visible to owners and users with access')}>
                    {getDatasetAccessTypeLabel(t, OutputPortAccessType.Private)}
                </Tooltip>
            ),
            value: DatasetAccess.Private,
        },
    ];
};

export function DatasetForm({ mode, modalCallbackOnSubmit, formRef, datasetId, dataProductId, dataOutputId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: currentDataset, isFetching: isFetchingInitialValues } = useGetOutputPortQuery(
        { id: datasetId || '', dataProductId: dataProductId || '' },
        {
            skip: mode === 'create' || !datasetId || !dataProductId,
        },
    );
    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductQuery(dataProductId || '', {
        skip: mode === 'edit' || !dataProductId,
    });
    const { data: lifecycles = undefined, isFetching: isFetchingLifecycles } = useGetDataProductsLifecyclesQuery();
    const { data: { users = [] } = {}, isFetching: isFetchingUsers } = useGetUsersQuery();
    const { data: { tags: availableTags = [] } = {}, isFetching: isFetchingTags } = useGetTagsQuery();
    const [createDataset, { isLoading: isCreating }] = useCreateOutputPortMutation();
    const [requestDatasetsAccessForDataOutput] = useLinkOutputPortToTechnicalAssetMutation();
    const [updateDataset, { isLoading: isUpdating }] = useUpdateOutputPortMutation();
    const [deleteDataset, { isLoading: isArchiving }] = useRemoveOutputPortMutation();
    const [sanitizeResourceName, { data: sanitizedResourceName }] = useLazySanitizeResourceNameQuery();
    const [validateResourceName] = useLazyValidateResourceNameQuery();
    const { data: constraints } = useResourceNameConstraintsQuery();

    const [form] = Form.useForm<CreateOutputPortRequest>();
    const datasetNameValue = Form.useWatch('name', form);

    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);

    const { data: create_access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT });
    const { data: update_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const { data: delete_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__DELETE,
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
    const tagSelectOptions = availableTags.map((tag) => ({ label: tag.value, value: tag.id }));

    const onFinish: FormProps<CreateOutputPortRequest>['onFinish'] = async (values) => {
        try {
            if (mode === 'create' && dataProduct) {
                const request: CreateOutputPortRequest = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    owners: values.owners,
                    tag_ids: values.tag_ids ?? [],
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };
                const response = await createDataset({
                    dataProductId: dataProduct.id,
                    createOutputPortRequest: request,
                }).unwrap();

                modalCallbackOnSubmit?.();
                dispatchMessage({ content: t('Output Port created successfully'), type: 'success' });
                // If dataProductId was provided, navigate back to the Data Product page
                if (dataOutputId && dataProductId) {
                    await requestDatasetsAccessForDataOutput({
                        dataProductId,
                        outputPortId: response.id,
                        linkTechnicalAssetToOutputPortRequest: {
                            technical_asset_id: dataOutputId,
                        },
                    });
                    navigate(createDataOutputIdPath(dataOutputId, dataProductId));
                } else {
                    if (dataProductId && !datasetId) {
                        navigate(createDataProductIdPath(dataProductId, TabKeys.OutputPorts));
                    } else {
                        navigate(createOutputPortPath(dataProductId || '', response.id));
                    }
                }
            } else if (mode === 'edit' && datasetId && currentDataset) {
                if (!canEdit) {
                    dispatchMessage({ content: t('You are not allowed to edit this Output Port'), type: 'error' });
                    return;
                }

                const request: DatasetUpdate = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    tag_ids: values.tag_ids,
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };

                const response = await updateDataset({
                    datasetUpdate: request,
                    id: datasetId,
                    dataProductId: currentDataset.data_product_id,
                }).unwrap();
                dispatchMessage({ content: t('Output Port updated successfully'), type: 'success' });

                navigate(createOutputPortPath(currentDataset.data_product_id, response.id));
            }
            form.resetFields();
        } catch (_e) {
            const errorMessage =
                mode === 'edit' ? t('Failed to update Output Port') : t('Failed to create Output Port');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && datasetId && dataProductId) {
            navigate(createMarketplaceOutputPortPath(datasetId, dataProductId));
        } else if (dataOutputId && dataProductId) {
            navigate(createOutputPortPath(dataOutputId, dataProductId));
        } else {
            navigate(ApplicationPaths.Marketplace);
        }
    };

    const onFinishFailed: FormProps<CreateOutputPortRequest>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const handleDeleteDataset = async () => {
        if (canDelete && currentDataset) {
            try {
                await deleteDataset({ dataProductId: currentDataset.data_product_id, id: currentDataset.id }).unwrap();
                dispatchMessage({ content: t('Output Port deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.Marketplace);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete Output Port, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    const fetchNamespaceDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), DEBOUNCE);

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
            form.setFieldValue('namespace', sanitizedResourceName?.resource_name);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditNamespace, sanitizedResourceName]);

    const validateResourceNameCallback = useCallback(
        (resourceName: string) =>
            validateResourceName({ resourceName: resourceName, model: ResourceNameModel.OutputPort }).unwrap(),
        [validateResourceName],
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
        lifecycle_id: currentDataset?.lifecycle?.id,
        tag_ids: currentDataset?.tags.map((tag) => tag.id),
        owners: ownerIds,
    };

    return (
        <Form<CreateOutputPortRequest>
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
            <Form.Item<CreateOutputPortRequest>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Output Port')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Output Port'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <ResourceNameFormItem
                form={form}
                tooltip={t('The namespace of the Output Port')}
                max_length={constraints?.max_length}
                editToggleDisabled={mode === 'edit'}
                canEditResourceName={canEditNamespace}
                toggleCanEditResourceName={() => setCanEditNamespace((prev) => !prev)}
                validationRequired={mode === 'create'}
                validateResourceName={validateResourceNameCallback}
            />
            {mode === 'create' && (
                <Form.Item<CreateOutputPortRequest>
                    name={'owners'}
                    label={t('Owners')}
                    tooltip={t('The owners of the Output Port')}
                    rules={[
                        {
                            required: true,
                            message: t('Please select at least one owner for the Output Port'),
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
            <Form.Item<CreateOutputPortRequest>
                name={'lifecycle_id'}
                label={t('Status')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the status of the Output Port'),
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
            <Form.Item<CreateOutputPortRequest>
                name={'access_type'}
                label={t('Access Type')}
                tooltip={t('The access type of the Output Port')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the access type of the Output Port'),
                    },
                ]}
            >
                <Radio.Group options={accessTypeOptions} />
            </Form.Item>
            <Form.Item<CreateOutputPortRequest> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select Output Port tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabel }}
                />
            </Form.Item>
            <Form.Item<CreateOutputPortRequest>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the Output Port')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Output Port'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than {{length}} characters', {
                            length: MAX_DESCRIPTION_INPUT_LENGTH,
                        }),
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
                                title={t('Are you sure you want to delete this Output Port?')}
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
