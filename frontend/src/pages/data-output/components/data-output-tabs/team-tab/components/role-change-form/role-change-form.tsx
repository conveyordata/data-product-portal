import { Form, FormProps, Select } from 'antd';
import styles from './role-change-form.module.scss';
// import {
//     DataOutputMembershipRole,
//     DataOutputMembershipRoleType,
//     DataOutputUserMembership,
// } from '@/types/data-output-membership';
import { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';

type UserRoleForm = {
    role: DataOutputMembershipRoleType;
};

type Props = {
    userId: string;
    initialRole: DataOutputMembershipRoleType;
    dataOutputUsers: DataOutputUserMembership[];
    onRoleChange: (role: DataOutputMembershipRoleType) => void;
    isDisabled?: boolean;
};

function getRoleOptions(t: TFunction) {
    return [
        {
            label: t('Owner'),
            value: DataOutputMembershipRole.Owner,
        },
        {
            label: t('Member'),
            value: DataOutputMembershipRole.Member,
        },
    ];
}

export function RoleChangeForm({ userId, initialRole, onRoleChange, isDisabled = true }: Props) {
    const { t } = useTranslation();
    const [dataOutputRoleForm] = Form.useForm<UserRoleForm>();
    const DATA_PRODUCT_ROLES = getRoleOptions(t);

    const handleRoleChange: FormProps<UserRoleForm>['onFinish'] = ({ role }) => {
        if (role !== initialRole) {
            onRoleChange(role);
        }
    };

    return (
        <Form<UserRoleForm> form={dataOutputRoleForm} initialValues={{ role: initialRole }} disabled={isDisabled}>
            <Form.Item<UserRoleForm> name={'role'} className={styles.selectRoleWrapper}>
                <Select onSelect={(value) => handleRoleChange({ role: value as DataOutputMembershipRole })}>
                    {DATA_PRODUCT_ROLES.map((role) => (
                        <Select.Option key={`${role.value}-${userId}`} value={role.value}>
                            {role.label}
                        </Select.Option>
                    ))}
                </Select>
            </Form.Item>
        </Form>
    );
}
