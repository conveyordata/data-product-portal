import { Button, Form, Input } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import styles from '@/pages/roles/components/create-role-modal.module.scss';
import { useUpdateRoleMutation } from '@/store/features/roles/roles-api-slice.ts';
import type { RoleContract } from '@/types/roles';

type Props = {
    role: RoleContract;
    isOpen: boolean;
    onClose: () => void;
};
export function ModifyRoleModal({ role, isOpen, onClose }: Props) {
    const { t } = useTranslation();

    const [updateRole, { isLoading }] = useUpdateRoleMutation();
    const [form] = Form.useForm();

    const title = useMemo(() => {
        switch (role.scope) {
            case 'global':
                return t('Update {{ name }} global role', { name: role.name });
            case 'data_product':
                return t('Update {{ name }} data product role', { name: role.name });
            case 'dataset':
                return t('Update {{ name }} dataset role', { name: role.name });
        }
    }, [role, t]);

    const handleCancel = (): void => {
        onClose();
        form.resetFields();
    };

    const handleSubmit = (): void => {
        form.validateFields()
            .then(() => {
                const request = {
                    id: role.id,
                    name: form.getFieldValue('name'),
                    description: form.getFieldValue('description'),
                };
                return updateRole(request);
            })
            .then(onClose);
    };

    const footer = [
        <Button className={styles.formButton} key="cancel" onClick={handleCancel}>
            {t('Cancel')}
        </Button>,
        <Button className={styles.formButton} key="submit" onClick={handleSubmit} type="primary" loading={isLoading}>
            {t('Update')}
        </Button>,
    ];

    return (
        <FormModal title={title} isOpen={isOpen} onClose={onClose} footer={footer}>
            <Form
                form={form}
                labelCol={FORM_GRID_WRAPPER_COLS}
                layout="vertical"
                initialValues={{ name: role.name, description: role.description }}
            >
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
