import { Button, Form, FormProps, Input, Popconfirm, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { DataOutputConfiguration, DataOutputCreateFormSchema } from '@/types/data-output';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation.ts';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useGetDataOutputByIdQuery, useRemoveDataOutputMutation, useUpdateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import TextArea from 'antd/es/input/TextArea';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { getIsDataProductOwner } from '@/utils/data-product-user-role.helper';
import { DataOutputUpdateRequest } from '@/types/data-output/data-output-update.contract';
import { ApiUrl, buildUrl } from '@/api/api-urls';

type Props = {
    mode: 'edit';
    dataOutputId: string
};

export function DataOutputForm({ mode, dataOutputId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { data: currentDataOutput, isFetching: isFetchingInitialValues } = useGetDataOutputByIdQuery(
        dataOutputId || '',
        {
            skip: !dataOutputId,
        },
    );
    const { data: dataProduct } = useGetDataProductByIdQuery(currentDataOutput?.owner.id ?? "", {skip: !currentDataOutput?.owner.id || isFetchingInitialValues || !dataOutputId});
    const currentUser = useSelector(selectCurrentUser);
    const [updateDataOutput, { isLoading: isUpdating }] = useUpdateDataOutputMutation();
    const [archiveDataOutput, { isLoading: isArchiving }] = useRemoveDataOutputMutation();
    const [form] = Form.useForm<DataOutputCreateFormSchema & DataOutputConfiguration>();
    const canEditForm = Boolean(
            dataProduct &&
            currentUser?.id &&
            (getIsDataProductOwner(dataProduct, currentUser?.id) || currentUser?.is_admin),
    );
    const canFillInForm = canEditForm;
    const isLoading = isFetchingInitialValues;

    const handleArchiveDataProduct = async () => {
        if (canEditForm && currentDataOutput) {
            try {
                await archiveDataOutput(currentDataOutput?.id).unwrap();
                dispatchMessage({ content: t('Data output archived successfully'), type: 'success' });
                navigate(createDataProductIdPath(dataProduct!.id));
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to archive data output, please try again later'),
                    type: 'error',
                });
            }
        }
    };
    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (dataOutputId && currentDataOutput) {
                if (!canEditForm) {
                    dispatchMessage({ content: t('You are not allowed to edit this data output'), type: 'error' });
                    return;
                };

                // TODO Figure out what fields are updateable and which are not
                const request: DataOutputUpdateRequest = {
                    name: values.name,
                    description: values.description,
                };
                console.log(buildUrl(ApiUrl.DataOutputGet, { dataOutputId: dataOutputId }),)
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

    useEffect(() => {
        if (currentDataOutput) {
            form.setFieldsValue({
                owner_id: currentDataOutput.owner_id,
                name: currentDataOutput.name,
                description: currentDataOutput.description,
            });
        }
    }, [currentDataOutput, mode]);

    return (
        <Form
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onSubmit}
            onFinishFailed={onSubmitFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            labelWrap
            disabled={isLoading || !canFillInForm}
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
                <TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {mode === 'edit' ? t('Edit') : t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Cancel')}
                    </Button>
                    {canEditForm && (
                        <Popconfirm
                            title={t('Are you sure you want to archive this data output?')}
                            onConfirm={handleArchiveDataProduct}
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
