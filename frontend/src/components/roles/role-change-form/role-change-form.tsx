import { Flex, Select } from 'antd';

import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import type { RoleContract } from '@/types/roles';

import styles from './role-change-form.module.scss';

type Props = {
    initialRole: RoleContract;
    onRoleChange: (role: RoleContract) => void;
    disabled?: boolean;
    scope: 'data_product' | 'dataset';
};
export function RoleChangeForm({ initialRole, onRoleChange, disabled = true, scope }: Props) {
    const { data: roles, isLoading } = useGetRolesQuery(scope);

    const options = roles?.map((role) => ({ label: role.name, value: role.id }));
    return (
        <Flex className={styles.selectRoleWrapper}>
            <Select
                className={styles.selectRoleInput}
                disabled={disabled}
                loading={isLoading}
                options={options}
                defaultValue={initialRole.id}
                onChange={(id: string) => {
                    const selectedRole = roles?.find((role) => role.id === id);
                    if (selectedRole) {
                        onRoleChange(selectedRole);
                    }
                }}
            />
        </Flex>
    );
}
