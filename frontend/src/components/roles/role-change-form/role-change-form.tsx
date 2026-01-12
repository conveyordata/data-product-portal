import { Flex, Select } from 'antd';

import { type Role, type Scope, useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi';

import styles from './role-change-form.module.scss';

type Props = {
    initialRole: Role;
    onRoleChange: (role: Role) => void;
    disabled?: boolean;
    scope: Scope;
};
export function RoleChangeForm({ initialRole, onRoleChange, disabled = true, scope }: Props) {
    const { data: { roles = [] } = {}, isLoading } = useGetRolesQuery(scope);

    const options = roles.map((role) => ({ label: role.name, value: role.id }));
    return (
        <Flex className={styles.selectRoleWrapper}>
            <Select
                className={styles.selectRoleInput}
                disabled={disabled}
                loading={isLoading}
                options={options}
                defaultValue={initialRole.id}
                onChange={(id: string) => {
                    const selectedRole = roles.find((role) => role.id === id);
                    if (selectedRole) {
                        onRoleChange(selectedRole);
                    }
                }}
            />
        </Flex>
    );
}
