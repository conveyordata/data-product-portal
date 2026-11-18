import { Flex, Select } from 'antd';
import { useTranslation } from 'react-i18next';

import { type Role, type Scope, useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi';
import { Prototype } from '@/types/roles';

import styles from './role-change-form.module.scss';

type Props = {
    role: Role | null;
    onRoleChange: (role: Role) => void;
    disabled?: boolean;
    ariaLabel?: string;
    allowOwner?: boolean;
    scope: Scope;
};
export function RoleChangeForm({ role, onRoleChange, disabled = true, scope, ariaLabel, allowOwner = true }: Props) {
    const { t } = useTranslation();
    const { data: { roles = [] } = {}, isLoading } = useGetRolesQuery(scope);

    const options = roles.map((role) => ({
        label: role.name,
        value: role.id,
        disabled: !allowOwner && role.prototype === Prototype.OWNER,
    }));
    return (
        <Flex className={styles.selectRoleWrapper}>
            <Select
                className={styles.selectRoleInput}
                aria-label={ariaLabel}
                disabled={disabled}
                loading={isLoading}
                options={options}
                value={role?.id}
                placeholder={t('No role assigned')}
                onChange={(id: string) => {
                    const selectedRole = roles.find((role) => role.id === id);
                    if (selectedRole && (allowOwner || selectedRole.prototype !== Prototype.OWNER)) {
                        onRoleChange(selectedRole);
                    }
                }}
            />
        </Flex>
    );
}
