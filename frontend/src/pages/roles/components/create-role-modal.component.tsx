import { Button, Form, Input } from 'antd';
import { useTranslation } from 'react-i18next';

import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { useCreateRoleMutation } from '@/store/features/roles/roles-api-slice';
import type { Scope } from '@/types/roles';
import styles from './create-role-modal.module.scss';

type Props = {
    scope: Scope;
    title: string;
    isOpen: boolean;
    onClose: () => void;
};
export function CreateRoleModal({ scope, title, isOpen, onClose }: Props) {
    const { t } = useTranslation();

    const [createRole, { isLoading }] = useCreateRoleMutation();
    const [form] = Form.useForm();

    const handleCancel = (): void => {
        onClose();
        form.resetFields();
    };

    const handleSubmit = (): void => {
        form.validateFields()
            .then(() => {
                const request = {
                    name: form.getFieldValue('name'),
                    scope: scope,
                    description: form.getFieldValue('description'),
                    permissions: [],
                };
                return createRole(request);
            })
            .then(handleCancel);
    };

    const footer = [
        <Button className={styles.formButton} key="cancel" onClick={handleCancel}>
            {t('Cancel')}
        </Button>,
        <Button className={styles.formButton} key="submit" onClick={handleSubmit} type="primary" loading={isLoading}>
            {t('Create')}
        </Button>,
    ];

    return (
        <FormModal title={title} isOpen={isOpen} onClose={onClose} footer={footer}>
            <Form form={form} labelCol={FORM_GRID_WRAPPER_COLS} layout="vertical">
                <Form.Item
                    name={'name'}
                    label={t('Name')}
                    tooltip={t('The name of your role')}
                    rules={[
                        {
                            required: true,
                            message: t('Please provide a name for your role'),
                        },
                    ]}
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    name={'description'}
                    label={t('Description')}
                    tooltip={t('A description for your role')}
                    rules={[
                        {
                            required: true,
                            message: t('Please provide a description for your role'),
                        },
                        {
                            max: MAX_DESCRIPTION_INPUT_LENGTH,
                            message: t('Description must be less than {{length}} characters', {
                                length: MAX_DESCRIPTION_INPUT_LENGTH,
                            }),
                        },
                    ]}
                >
                    <Input.TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
                </Form.Item>
            </Form>
        </FormModal>
    );
}
