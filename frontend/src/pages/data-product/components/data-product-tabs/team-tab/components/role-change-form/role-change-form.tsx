import { Form, FormProps, Select } from 'antd';
import { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';

import {
    DataProductMembershipRole,
    DataProductMembershipRoleType,
    DataProductUserMembership,
} from '@/types/data-product-membership';

import styles from './role-change-form.module.scss';

type UserRoleForm = {
    role: DataProductMembershipRoleType;
};

type Props = {
    userId: string;
    initialRole: DataProductMembershipRoleType;
    dataProductUsers: DataProductUserMembership[];
    onRoleChange: (role: DataProductMembershipRoleType) => void;
    isDisabled?: boolean;
};

function getRoleOptions(t: TFunction) {
    return [
        {
            label: t('Owner'),
            value: DataProductMembershipRole.Owner,
        },
        {
            label: t('Member'),
            value: DataProductMembershipRole.Member,
        },
    ];
}

export function RoleChangeForm({ userId, initialRole, onRoleChange, isDisabled = true }: Props) {
    const { t } = useTranslation();
    const [dataProductRoleForm] = Form.useForm<UserRoleForm>();
    const DATA_PRODUCT_ROLES = getRoleOptions(t);

    const handleRoleChange: FormProps<UserRoleForm>['onFinish'] = ({ role }) => {
        if (role !== initialRole) {
            onRoleChange(role);
        }
    };

    return (
        <Form<UserRoleForm> form={dataProductRoleForm} initialValues={{ role: initialRole }} disabled={isDisabled}>
            <Form.Item<UserRoleForm> name={'role'} className={styles.selectRoleWrapper}>
                <Select onSelect={(value) => handleRoleChange({ role: value as DataProductMembershipRole })}>
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
