import { Checkbox, Select, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import type { UsersGet } from '@/store/api/services/generated/usersApi.ts';
import { type GlobalRoleAssignment, Prototype } from '@/types/roles';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';
import styles from './people-table.module.scss';

type SelectorProps = {
    role: GlobalRoleAssignment | null;
    everyone: Role | undefined;
    options: { label: string; value: string }[];
    onChange: (value: string) => void;
    disabled?: boolean;
};
function RoleSelector({ role, everyone, options, onChange, disabled = false }: SelectorProps) {
    return (
        <Select
            className={styles.select}
            defaultValue={role?.role.name ?? everyone?.name}
            options={options}
            onChange={(value: string) => onChange(value)}
            disabled={disabled}
        />
    );
}

export const getPeopleTableColumns = ({
    t,
    users: data,
    canAssignRole,
    allRoles,
    onChange,
    changeCheckbox,
}: {
    t: TFunction;
    users: UsersGet[];
    canAssignRole: boolean;
    allRoles: Role[];
    onChange: (user_id: string, value: string, original: GlobalRoleAssignment | null) => void;
    changeCheckbox: (user_id: string, can_become_admin: boolean) => void;
}): TableColumnsType<UsersGet> => {
    const sorter = new Sorter<UsersGet>();
    const everyone = allRoles.find((role) => role.prototype === Prototype.EVERYONE);
    const options = allRoles.map((role) => ({
        label: role.name,
        value: role.prototype === Prototype.EVERYONE ? '' : role.id,
    }));

    const columns: TableColumnsType<UsersGet> = [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: { showTitle: false },
            width: 4,
            render: (_, record) => {
                return <TableCellItem text={`${record.first_name} ${record.last_name}`} />;
            },
            ...new FilterSettings(data, (user) => (user.first_name !== null ? user.first_name : '')),
            sorter: sorter.stringSorter((user) => user.first_name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Email'),
            dataIndex: 'email',
            ellipsis: { showTitle: false },
            width: 4,
            render: (email) => {
                return <TableCellItem text={email} />;
            },
            ...new FilterSettings(data, (user) => (user.email !== null ? user.email : '')),
            sorter: sorter.stringSorter((user) => user.email),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Global Role'),
            dataIndex: 'global_role',
            ellipsis: { showTitle: false },
            width: 4,
            render: (role: GlobalRoleAssignment | null, user: UsersGet) => {
                let name = role?.role.name;
                if (role?.role.prototype === Prototype.ADMIN) {
                    name = everyone?.name;
                }
                if (canAssignRole) {
                    return (
                        <TableCellItem>
                            <RoleSelector
                                everyone={everyone}
                                role={role}
                                onChange={(value: string) => onChange(user.id, value, role)}
                                options={options}
                            />
                        </TableCellItem>
                    );
                }
                return <TableCellItem text={name || everyone?.name} />;
            },
        },
    ];

    if (canAssignRole) {
        columns.push({
            title: t('Can become admin'),
            dataIndex: 'can_become_admin',
            ellipsis: { showTitle: false },
            width: 2,
            render: (_, user) => {
                return (
                    <Checkbox
                        checked={user.can_become_admin}
                        onChange={(e) => changeCheckbox(user.id, e.target.checked)}
                    />
                );
            },
        });
    }

    return columns;
};
