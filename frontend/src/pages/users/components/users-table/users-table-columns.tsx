import { Select, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { GlobalRoleAssignmentContract, RoleContract } from '@/types/roles/role.contract';
import type { UsersGetContract } from '@/types/users/user.contract';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';
import styles from './users-table.module.scss';

export const getUserTableColumns = ({
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
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        // This is an empty column to match to give a small indentation to the table and match the datasets table icon column
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: {
                showTitle: false,
            },
            render: (_, record) => {
                return <TableCellItem text={`${record.first_name} ${record.last_name}`} />;
            },
            ...new FilterSettings(data, (user) => (user.first_name !== null ? user.first_name : '')),
            sorter: sorter.stringSorter((user) => user.first_name),
            defaultSortOrder: 'ascend',
            width: '25%',
        },
        {
            title: t('Email'),
            dataIndex: 'email',
            ellipsis: {
                showTitle: false,
            },
            render: (email) => {
                return <TableCellItem text={email} />;
            },
            ...new FilterSettings(data, (user) => (user.email !== null ? user.email : '')),
            sorter: sorter.stringSorter((user) => user.email),
            defaultSortOrder: 'ascend',
            width: '25%',
        },
        {
            title: t('Global Role'),
            dataIndex: 'global_role',
            ellipsis: {
                showTitle: false,
            },
            render: (role: GlobalRoleAssignmentContract | null, record) => {
                if (canAssignRole) {
                    const options = allRoles.map((role) => ({
                        label: role.name,
                        value: role.id,
                    }));
                    return (
                        <TableCellItem>
                            <Select
                                onChange={(value: string) => onChange(record.id, value, role)}
                                defaultValue={role?.role.name}
                                className={styles.select}
                                options={options}
                                allowClear
                            />
                        </TableCellItem>
                    );
                }
                return <TableCellItem text={role?.role.name || ''} />;
            },
            // ...new FilterSettings(data, (user) => (user.email !== null ? user.email : '')),
            // sorter: sorter.stringSorter((user) => user.global_roles),
            // defaultSortOrder: 'ascend',
            width: '25%',
        },
    ];
};
