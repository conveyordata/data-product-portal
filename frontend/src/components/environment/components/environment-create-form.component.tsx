import { Button, Form, FormProps, Input, Switch, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './environment-create.module.scss';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useNavigate } from 'react-router-dom';
import { ApplicationPaths } from '@/types/navigation.ts';
import { EnvironmentCreateFormSchema } from '@/types/environment';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { useCreateEnvironmentMutation } from '@/store/features/environments/environments-api-slice';

export function EnvironmentCreateForm() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const [createEnvironment, { isLoading: isCreating }] = useCreateEnvironmentMutation();

    const [form] = Form.useForm<EnvironmentCreateFormSchema>();

    const onCancel = () => {
        form.resetFields();
        navigate(ApplicationPaths.Environments);
    };

    const onFinishFailed: FormProps<EnvironmentCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onFinish: FormProps<EnvironmentCreateFormSchema>['onFinish'] = async (values) => {
        try {
            const request: EnvironmentCreateFormSchema = {
                name: values.name,
                is_default: values.is_default || false,
            };

            await createEnvironment(request).unwrap();
            dispatchMessage({ content: t('Environment created successfully'), type: 'success' });
            navigate(ApplicationPaths.Environments);
        } catch (e) {
            const errorMessage = t('Failed to create environment');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    return (
        <Form<EnvironmentCreateFormSchema>
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete={'off'}
            requiredMark={false}
            labelWrap
            disabled={isCreating}
        >
            <Form.Item<EnvironmentCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your environment')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the environment name'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<EnvironmentCreateFormSchema>
                name={'is_default'}
                valuePropName="checked"
                label={t('Is a default environment?')}
            >
                <Switch />
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button className={styles.formButton} type="primary" htmlType={'submit'} loading={isCreating}>
                        {t('Create')}
                    </Button>
                    <Button className={styles.formButton} type="default" onClick={onCancel} loading={isCreating}>
                        {t('Cancel')}
                    </Button>
                </Space>
            </Form.Item>
        </Form>
    );
}
