import { Button, CheckboxOptionType, Form, FormProps, Input, Popconfirm, Radio, Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './dataset-form.module.scss';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { TagCreate } from '@/types/tag';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
import { useGetAllBusinessAreasQuery } from '@/store/features/business-areas/business-areas-api-slice.ts';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useSelector } from 'react-redux';
import {
    useCreateDatasetMutation,
    useGetDatasetByIdQuery,
    useRemoveDatasetMutation,
    useUpdateDatasetMutation,
} from '@/store/features/datasets/datasets-api-slice.ts';
import { DatasetAccess, DatasetCreateFormSchema, DatasetCreateRequest, DatasetUpdateRequest } from '@/types/dataset';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { getDatasetOwnerIds, getIsDatasetOwner } from '@/utils/dataset-user.helper.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import { useGetAllDataProductLifecyclesQuery } from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';

type Props = {
    mode: 'create' | 'edit';
    datasetId?: string;
};

const { TextArea } = Input;

const getAccessTypeOptions = () => [
    {
        value: DatasetAccess.Public,
        label: getDatasetAccessTypeLabel(DatasetAccess.Public),
    },
    {
        value: DatasetAccess.Restricted,
        label: getDatasetAccessTypeLabel(DatasetAccess.Restricted),
    },
];

export function DatasetForm({ mode, datasetId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);
    const { data: currentDataset, isFetching: isFetchingInitialValues } = useGetDatasetByIdQuery(datasetId || '', {
        skip: mode === 'create' || !datasetId,
    });
    const { data: businessAreas = [], isFetching: isFetchingBusinessAreas } = useGetAllBusinessAreasQuery();
    const { data: lifecycles = [], isFetching: isFetchingLifecycles } = useGetAllDataProductLifecyclesQuery();
    const { data: users = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const [createDataset, { isLoading: isCreating }] = useCreateDatasetMutation();
    const [updateDataset, { isLoading: isUpdating }] = useUpdateDatasetMutation();
    const [archiveDataset, { isLoading: isArchiving }] = useRemoveDatasetMutation();
    const [form] = Form.useForm<DatasetCreateFormSchema>();
    const datasetNameValue = Form.useWatch('name', form);

    const canEditForm = Boolean(
        mode === 'edit' &&
            currentDataset &&
            currentUser?.id &&
            (getIsDatasetOwner(currentDataset, currentUser?.id) || currentUser?.is_admin),
    );
    const canFillInForm = mode === 'create' || canEditForm;

    const isLoading = isCreating || isUpdating || isCreating || isUpdating || isFetchingInitialValues || isFetchingTags;

    const accessTypeOptions: CheckboxOptionType<DatasetAccess>[] = useMemo(() => getAccessTypeOptions(), []);
    const businessAreaSelectOptions = businessAreas.map((area) => ({ label: area.name, value: area.id }));
    const userSelectOptions = users.map((user) => ({ label: user.email, value: user.id }));
    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];

    const onFinish: FormProps<DatasetCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (mode === 'create') {
                const request: DatasetCreateRequest = {
                    name: values.name,
                    external_id: values.external_id,
                    description: values.description,
                    owners: values.owners,
                    tag_ids: values.tag_ids ?? [],
                    business_area_id: values.business_area_id,
                    lifecycle_id: values.lifecycle_id,
                    access_type: values.access_type,
                };
                const response = await createDataset(request).unwrap();
                dispatchMessage({ content: t('Dataset created successfully'), type: 'success' });

                navigate(createDatasetIdPath(response.id));
            } else if (mode === 'edit' && datasetId) {
                if (!canEditForm) {
                    dispatchMessage({ content: t('You are not allowed to edit this dataset'), type: 'error' });
                    return;
                }

                const request: DatasetUpdateRequest = {
                    name: values.name,
                    external_id: values.external_id,
                    description: values.description,
                    owners: values.owners,
                    tag_ids: values.tag_ids,
                    business_area_id: values.business_area_id,
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

    const handleArchiveDataset = async () => {
        if (canEditForm && currentDataset) {
            try {
                await archiveDataset(currentDataset?.id).unwrap();
                dispatchMessage({ content: t('Dataset archived successfully'), type: 'success' });
                navigate(ApplicationPaths.Datasets);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to archive dataset, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    useEffect(() => {
        if (mode === 'create') {
            form.setFieldsValue({ external_id: generateExternalIdFromName(datasetNameValue ?? '') });
        }
    }, [datasetNameValue, form, mode]);

    useEffect(() => {
        if (currentDataset && mode === 'edit') {
            form.setFieldsValue({
                external_id: currentDataset.external_id,
                name: currentDataset.name,
                description: currentDataset.description,
                access_type: currentDataset.access_type,
                business_area_id: currentDataset.business_area.id,
                tag_ids: currentDataset.tags.map((tag) => tag.id),
                lifecycle_id: currentDataset.lifecycle.id,
                owners: getDatasetOwnerIds(currentDataset),
            });
        }
    }, [currentDataset, mode, form]);

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
            disabled={isLoading || !canFillInForm}
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
            {/*Disabled field that will render an external ID everytime the name changes*/}
            <Form.Item<DatasetCreateFormSchema>
                required
                name={'external_id'}
                label={t('External ID')}
                tooltip={t('The external ID of the dataset')}
            >
                <Input disabled />
            </Form.Item>
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
                    allowClear
                    tokenSeparators={[',']}
                />
            </Form.Item>
            <Form.Item<DatasetCreateFormSchema>
                name={'business_area_id'}
                label={t('Business Area')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the business area of the dataset'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingBusinessAreas}
                    options={businessAreaSelectOptions}
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
                    mode={'tags'}
                    options={tagSelectOptions}
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
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreating || isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {mode === 'edit' ? t('Edit') : t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isCreating || isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Cancel')}
                    </Button>
                    {canEditForm && (
                        <Popconfirm
                            title={t('Are you sure you want to archive this dataset?')}
                            onConfirm={handleArchiveDataset}
                            okText={t('Yes')}
                            cancelText={t('No')}
                        >
                            <Button
                                className={styles.formButton}
                                type="default"
                                danger
                                loading={isArchiving}
                                disabled={isLoading}
                            >
                                {t('Archive')}
                            </Button>
                        </Popconfirm>
                    )}
                </Space>
            </Form.Item>
        </Form>
    );
}
