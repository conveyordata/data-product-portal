import { Select, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { type GlobalRoleAssignmentContract, Prototype, type RoleContract } from '@/types/roles/role.contract';
import type { UserContract, UsersGetContract } from '@/types/users/user.contract';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';
import styles from './people-table.module.scss';

type SelectorProps = {
    role: GlobalRoleAssignmentContract | null;
    everyone: RoleContract | undefined;
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
}: {
    t: TFunction;
    users: UsersGetContract;
    canAssignRole: boolean;
    allRoles: RoleContract[];
    onChange: (user_id: string, value: string, original: GlobalRoleAssignmentContract | null) => void;
}): TableColumnsType<UsersGetContract[0]> => {
    const sorter = new Sorter<UsersGetContract[0]>();
    const everyone = allRoles.find((role) => role.prototype === Prototype.EVERYONE);
    const options = allRoles.map((role) => ({
        label: role.name,
        value: role.prototype === Prototype.EVERYONE ? '' : role.id,
    }));

    const numberOfAdmins = data.filter((user) => user.global_role?.role.prototype === Prototype.ADMIN).length;
    const lockAdmins = numberOfAdmins <= 1;

    return [
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
            render: (role: GlobalRoleAssignmentContract | null, user: UserContract) => {
                if (canAssignRole) {
                    const disabled = role?.role.prototype === Prototype.ADMIN && lockAdmins;

                    return (
                        <TableCellItem>
                            <RoleSelector
                                everyone={everyone}
                                role={role}
                                onChange={(value: string) => onChange(user.id, value, role)}
                                options={options}
                                disabled={disabled}
                            />
                        </TableCellItem>
                    );
                }
                return <TableCellItem text={role?.role.name || everyone?.name} />;
            },
        },
    ];
};
