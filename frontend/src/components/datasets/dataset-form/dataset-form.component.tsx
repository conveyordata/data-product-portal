import {
    Button,
    type CheckboxOptionType,
    Col,
    Form,
    type FormProps,
    Input,
    Popconfirm,
    Radio,
    Row,
    Select,
    Space,
    Tooltip,
} from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';

import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetAllDataProductLifecyclesQuery } from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import {
    useCreateDatasetMutation,
    useGetDatasetByIdQuery,
    useGetDatasetNamespaceLengthLimitsQuery,
    useLazyGetDatasetNamespaceSuggestionQuery,
    useLazyValidateDatasetNamespaceQuery,
    useRemoveDatasetMutation,
    useUpdateDatasetMutation,
} from '@/store/features/datasets/datasets-api-slice.ts';
import { useGetAllDomainsQuery } from '@/store/features/domains/domains-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import {
    DatasetAccess,
    DatasetCreateFormSchema,
    type DatasetCreateRequest,
    type DatasetUpdateRequest,
} from '@/types/dataset';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';
import { useGetDatasetOwnerIds } from '@/utils/dataset-user-role.helper.ts';
import { selectFilterOptionByLabel, selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';

import styles from './dataset-form.module.scss';

type Props = {
    mode: 'create' | 'edit';
    datasetId?: string;
};

const { TextArea } = Input;

const DEBOUNCE = 500;

const getAccessTypeOptions = (t: TFunction) => {
    return [
        {
            label: (
                <Tooltip title={t('Public datasets are visible to everyone and are free to use by anyone')}>
                    {getDatasetAccessTypeLabel(t, DatasetAccess.Public)}
                </Tooltip>
            ),
            value: DatasetAccess.Public,
        },
        {
            label: (
                <Tooltip title={t('Restricted datasets are visible to everyone but require permission to use')}>
                    {getDatasetAccessTypeLabel(t, DatasetAccess.Restricted)}
                </Tooltip>
            ),
            value: DatasetAccess.Restricted,
        },
        {
            label: (
                <Tooltip title={t('Private datasets are only visible to owners and users with access')}>
                    {getDatasetAccessTypeLabel(t, DatasetAccess.Private)}
                </Tooltip>
            ),
            value: DatasetAccess.Private,
        },
    ];
};

export function DatasetForm({ mode, datasetId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: currentDataset, isFetching: isFetchingInitialValues } = useGetDatasetByIdQuery(datasetId || '', {
        skip: mode === 'create' || !datasetId,
    });
    const { data: domains = [], isFetching: isFetchingDomains } = useGetAllDomainsQuery();
    const { data: lifecycles = [], isFetching: isFetchingLifecycles } = useGetAllDataProductLifecyclesQuery();
    const { data: users = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const [createDataset, { isLoading: isCreating }] = useCreateDatasetMutation();
    const [updateDataset, { isLoading: isUpdating }] = useUpdateDatasetMutation();
    const [deleteDataset, { isLoading: isArchiving }] = useRemoveDatasetMutation();
    const [fetchNamespace, { data: namespaceSuggestion, isFetching: isFetchingNamespaceSuggestion }] =
        useLazyGetDatasetNamespaceSuggestionQuery();
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

    const isLoading = isCreating || isUpdating || isCreating || isUpdating || isFetchingInitialValues || isFetchingTags;

    const accessTypeOptions: CheckboxOptionType<DatasetAccess>[] = useMemo(() => getAccessTypeOptions(t), [t]);
    const domainSelectOptions = domains.map((domain) => ({ label: domain.name, value: domain.id }));
    const userSelectOptions = users.map((user) => ({ label: user.email, value: user.id }));
    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];

    const onFinish: FormProps<DatasetCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (mode === 'create') {
                const request: DatasetCreateRequest = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    owners: values.owners,
                    tag_ids: values.tag_ids ?? [],
                    domain_id: values.domain_id,
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };
                const response = await createDataset(request).unwrap();
                dispatchMessage({ content: t('Dataset created successfully'), type: 'success' });

                navigate(createDatasetIdPath(response.id));
            } else if (mode === 'edit' && datasetId) {
                if (!canEdit) {
                    dispatchMessage({ content: t('You are not allowed to edit this dataset'), type: 'error' });
                    return;
                }

                const request: DatasetUpdateRequest = {
                    name: values.name,
                    namespace: values.namespace,
                    description: values.description,
                    owners: values.owners,
                    tag_ids: values.tag_ids,
                    domain_id: values.domain_id,
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };

                const response = await updateDataset({ dataset: request, id: datasetId }).unwrap();
                dispatchMessage({ content: t('Dataset updated successfully'), type: 'success' });

                navigate(createDatasetIdPath(response.id));
            }

            form.resetFields();
        } catch (_e) {
            const errorMessage = mode === 'edit' ? t('Failed to update dataset') : t('Failed to create dataset');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && datasetId) {
            navigate(createDatasetIdPath(datasetId));
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
                await deleteDataset(currentDataset?.id).unwrap();
                dispatchMessage({ content: t('Dataset deleted successfully'), type: 'success' });
                navigate(ApplicationPaths.Datasets);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete dataset, please try again later'),
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
    }, [form, mode, canEditNamespace, namespaceSuggestion, isFetchingNamespaceSuggestion, t]);

    const ownerIds = useGetDatasetOwnerIds(currentDataset?.id);

    useEffect(() => {
        if (currentDataset && mode === 'edit') {
            form.setFieldsValue({
                namespace: currentDataset.namespace,
                name: currentDataset.name,
                description: currentDataset.description,
                access_type: currentDataset.access_type,
                domain_id: currentDataset.domain.id,
                tag_ids: currentDataset.tags.map((tag) => tag.id),
                lifecycle_id: currentDataset.lifecycle.id,
                owners: ownerIds,
            });
        }
    }, [currentDataset, mode, form, ownerIds]);

    const validateNamespaceCallback = useCallback(
        (namespace: string) => validateNamespace(namespace).unwrap(),
        [validateNamespace],
    );

    return (
        <Form<DatasetCreateFormSchema>
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
            <Form.Item<DatasetCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your dataset')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the dataset'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <NamespaceFormItem
                form={form}
                tooltip={t('The namespace of the dataset')}
                max_length={namespaceLengthLimits?.max_length}
                editToggleDisabled={mode === 'edit'}
                canEditNamespace={canEditNamespace}
                toggleCanEditNamespace={() => setCanEditNamespace((prev) => !prev)}
                validationRequired={mode === 'create'}
                validateNamespace={validateNamespaceCallback}
            />
            <Form.Item<DatasetCreateFormSchema>
                name={'owners'}
                label={t('Owners')}
                tooltip={t('The owners of the dataset')}
                rules={[
                    {
                        required: true,
                        message: t('Please select at least one owner for the dataset'),
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
            <Form.Item<DatasetCreateFormSchema>
                name={'domain_id'}
                label={t('Domain')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the domain of the dataset'),
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
            <Form.Item<DatasetCreateFormSchema>
                name={'lifecycle_id'}
                label={t('Status')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the status of the dataset'),
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
            <Form.Item<DatasetCreateFormSchema>
                name={'access_type'}
                label={t('Access Type')}
                tooltip={t('The access type of the dataset')}
                initialValue={mode === 'create' ? DatasetAccess.Public : currentDataset?.access_type}
                rules={[
                    {
                        required: true,
                        message: t('Please select the access type of the dataset'),
                    },
                ]}
            >
                <Radio.Group options={accessTypeOptions} />
            </Form.Item>
            <Form.Item<DatasetCreateFormSchema> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select dataset tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    filterOption={selectFilterOptionByLabel}
                />
            </Form.Item>
            <Form.Item<DatasetCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the dataset')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the dataset'),
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
                                title={t('Are you sure you want to delete this dataset?')}
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
