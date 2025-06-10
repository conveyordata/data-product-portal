import { Button, Form, type FormProps, Input, Popconfirm, Select, Skeleton, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useGetDataOutputByIdQuery,
    useGetDataOutputNamespaceLengthLimitsQuery,
    useRemoveDataOutputMutation,
    useUpdateDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputConfiguration, DataOutputCreateFormSchema } from '@/types/data-output';
import type { DataOutputUpdateRequest } from '@/types/data-output/data-output-update.contract';
import { createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation';
import { selectFilterOptionByLabel } from '@/utils/form.helper';

import styles from './data-output-form.module.scss';

type Props = {
    mode: 'edit';
    dataOutputId: string;
};

export function DataOutputForm({ mode, dataOutputId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { data: currentDataOutput, isFetching: isFetchingInitialValues } = useGetDataOutputByIdQuery(
        dataOutputId || '',
        { skip: !dataOutputId },
    );
    const { data: dataProduct } = useGetDataProductByIdQuery(currentDataOutput?.owner.id ?? '', {
        skip: !currentDataOutput?.owner.id || isFetchingInitialValues || !dataOutputId,
    });
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const [updateDataOutput, { isLoading: isUpdating }] = useUpdateDataOutputMutation();
    const [deleteDataOutput, { isLoading: isArchiving }] = useRemoveDataOutputMutation();
    const [form] = Form.useForm<DataOutputCreateFormSchema & DataOutputConfiguration>();

    const { data: update_access } = useCheckAccessQuery(
        {
            resource: dataProduct?.id,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
        },
        { skip: !dataProduct?.id },
    );
    const { data: delete_access } = useCheckAccessQuery(
        {
            resource: dataProduct?.id,
            action: AuthorizationAction.DATA_PRODUCT__DELETE_DATA_OUTPUT,
        },
        { skip: !dataProduct?.id },
    );

    const canEdit = mode === 'edit' && (update_access?.allowed ?? false);
    const canDelete = mode === 'edit' && (delete_access?.allowed ?? false);

    const isLoading = isFetchingInitialValues || isFetchingTags;
    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];
    const { data: namespaceLengthLimits } = useGetDataOutputNamespaceLengthLimitsQuery();

    const handleDeleteDataOutput = async () => {
        if (canDelete && currentDataOutput && dataProduct) {
            try {
                await deleteDataOutput(currentDataOutput.id).unwrap();
                dispatchMessage({ content: t('Data output deleted successfully'), type: 'success' });
                navigate(createDataProductIdPath(dataProduct.id));
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to delete data output, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (dataOutputId && currentDataOutput) {
                if (!canEdit) {
                    dispatchMessage({ content: t('You are not allowed to edit this data output'), type: 'error' });
                    return;
                }

                // TODO Figure out what fields are updatable and which are not
                const request: DataOutputUpdateRequest = {
                    name: values.name,
                    description: values.description,
                    tag_ids: values.tag_ids ?? [],
                };
                const response = await updateDataOutput({
                    dataOutput: request,
                    dataOutputId: dataOutputId,
                }).unwrap();
                dispatchMessage({ content: t('Data output updated successfully'), type: 'success' });

                navigate(createDataOutputIdPath(response.id, currentDataOutput.owner.id));
            }

            form.resetFields();
        } catch (_e) {
            const errorMessage = 'Failed to create data output';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataOutputCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onCancel = () => {
        form.resetFields();
        if (dataOutputId && currentDataOutput) {
            navigate(createDataOutputIdPath(dataOutputId, currentDataOutput.owner.id));
        }
    };

    if (mode === 'edit' && !currentDataOutput) {
        return <Skeleton active />;
    }

    const initialValues = {
        namespace: currentDataOutput?.namespace,
        name: currentDataOutput?.name,
        description: currentDataOutput?.description,
        tag_ids: currentDataOutput?.tags.map((tag) => tag.id),
    };

    return (
        <Form
            form={form}
            labelWrap
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onSubmit}
            onFinishFailed={onSubmitFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            disabled={isLoading || !canEdit}
            initialValues={initialValues}
        >
            <Form.Item<DataOutputCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your data output')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the data output'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <NamespaceFormItem
                form={form}
                tooltip={t('The namespace of the data output')}
                max_length={namespaceLengthLimits?.max_length}
                editToggleDisabled
                canEditNamespace={false}
            />
            <Form.Item<DataOutputCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the data output')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the data output'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than 255 characters'),
                    },
                ]}
            >
                <Input.TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select data output tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    filterOption={selectFilterOptionByLabel}
                />
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isUpdating}
                        disabled={isLoading || !canEdit}
                    >
                        {mode === 'edit' ? t('Edit') : t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isUpdating}
                        disabled={isLoading || !canEdit}
                    >
                        {t('Cancel')}
                    </Button>
                    {canDelete && (
                        <Popconfirm
                            title={t('Are you sure you want to delete this data output?')}
                            onConfirm={handleDeleteDataOutput}
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
                                {t('Delete')}
                            </Button>
                        </Popconfirm>
                    )}
                </Space>
            </Form.Item>
        </Form>
    );
}
