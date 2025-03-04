import { Button, Flex, Form, FormProps, Input, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './general-form.module.scss';
import { CloseOutlined, EditOutlined, SaveOutlined } from '@ant-design/icons';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useEffect, useState } from 'react';
import {
    useGetGeneralSettingsQuery,
    useUpdateGeneralSettingsMutation,
} from '@/store/features/general-settings/general-settings-api-slice';
import { GeneralSettings } from '@/types/general-settings';

export function GeneralSettingsForm() {
    const { t } = useTranslation();
    const { data, isFetching } = useGetGeneralSettingsQuery();
    const [updateGeneralSettings, { isLoading: isUpdating }] = useUpdateGeneralSettingsMutation();
    const [form] = Form.useForm<GeneralSettings>();
    const [canEditForm, setCanEditForm] = useState(false);

    const isLoading = isFetching || isUpdating;

    useEffect(() => {
        if (data) {
            form.setFieldsValue(data);
        }
    }, [isFetching]);

    const onSubmit: FormProps<GeneralSettings>['onFinish'] = async (values) => {
        try {
            updateGeneralSettings(values);
            setCanEditForm(false);
            dispatchMessage({ content: t('Settings updated successfully'), type: 'success' });
        } catch (_) {
            form.resetFields();
            setCanEditForm(false);
            dispatchMessage({ content: t('Failed to update settings'), type: 'error' });
        }
    };

    const handleCancel = () => {
        form.resetFields();
        setCanEditForm(false);
    };

    const handleSave = () => {
        form.validateFields({ validateOnly: true })
            .then(() => {
                form.submit();
            })
            .catch(() => dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' }));
    };

    const handleEdit = () => {
        setCanEditForm(true);
    };

    const onSubmitFailed: FormProps<GeneralSettings>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    return (
        <Flex vertical className={styles.container}>
            <Flex className={styles.globalSettingsHeader}>
                <Typography.Title level={3}>{t('Customisation')}</Typography.Title>
                <Space>
                    {canEditForm ? (
                        <>
                            <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
                                Save
                            </Button>
                            <Button icon={<CloseOutlined />} onClick={handleCancel}>
                                Cancel
                            </Button>
                        </>
                    ) : (
                        <Button type="default" icon={<EditOutlined />} onClick={handleEdit}>
                            Edit
                        </Button>
                    )}
                </Space>
            </Flex>
            <Form
                form={form}
                layout="vertical"
                onFinish={onSubmit}
                onFinishFailed={onSubmitFailed}
                autoComplete={'off'}
                requiredMark={'optional'}
                labelWrap
                disabled={isLoading || !canEditForm}
                initialValues={data}
            >
                <Form.Item
                    name={'portal_name'}
                    label={t('Portal Name')}
                    tooltip={t('The name of the Data Product Portal')}
                    rules={[
                        {
                            required: true,
                            message: t('Please input the name of the Data Product Portal'),
                        },
                    ]}
                >
                    <Input onPressEnter={(e) => e.preventDefault()} />
                </Form.Item>
            </Form>
        </Flex>
    );
}
