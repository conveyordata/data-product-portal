import { Form, FormProps, Select } from 'antd';
import { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';

import { DatasetMembershipRole, DatasetMembershipRoleType, DatasetUserMembership } from '@/types/dataset-membership';

import styles from './role-change-form.module.scss';

type UserRoleForm = {
    role: DatasetMembershipRoleType;
};

type Props = {
    userId: string;
    initialRole: DatasetMembershipRoleType;
    datasetUsers: DatasetUserMembership[];
    onRoleChange: (role: DatasetMembershipRoleType) => void;
    isDisabled?: boolean;
};

function getRoleOptions(t: TFunction) {
    return [
        {
            label: t('Owner'),
            value: DatasetMembershipRole.Owner,
        },
    ];
}

export function RoleChangeForm({ userId, initialRole, onRoleChange, isDisabled = true }: Props) {
    const { t } = useTranslation();
    const [datasetRoleForm] = Form.useForm<UserRoleForm>();
    const DATASET_ROLES = getRoleOptions(t);

    const handleRoleChange: FormProps<UserRoleForm>['onFinish'] = ({ role }) => {
        if (role !== initialRole) {
            onRoleChange(role);
        }
    };

    return (
        <Form<UserRoleForm> form={datasetRoleForm} initialValues={{ role: initialRole }} disabled={isDisabled}>
            <Form.Item<UserRoleForm> name={'role'} className={styles.selectRoleWrapper}>
                <Select onSelect={(value) => handleRoleChange({ role: value as DatasetMembershipRole })}>
                    {DATASET_ROLES.map((role) => (
                        <Select.Option key={`${role.value}-${userId}`} value={role.value}>
                            {role.label}
                        </Select.Option>
                    ))}
                </Select>
            </Form.Item>
        </Form>
    );
}
