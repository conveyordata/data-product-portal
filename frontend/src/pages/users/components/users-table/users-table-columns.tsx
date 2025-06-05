import { Select, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

import { GlobalRoleAssignmentContract, RoleContract } from '@/types/roles/role.contract';
import { UsersGetContract } from '@/types/users/user.contract';
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
    onChange: (user_id: string, value: string[], originals: string[]) => void;
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
            dataIndex: 'global_roles',
            ellipsis: {
                showTitle: false,
            },
            render: (roles: GlobalRoleAssignmentContract[], record) => {
                if (canAssignRole) {
                    const options = allRoles.map((role) => ({
                        label: role.name,
                        value: role.id,
                    }));
                    const currentRole = roles.map((role: GlobalRoleAssignmentContract) => role.role.name);
                    const originals = roles.map((role: GlobalRoleAssignmentContract) => role.id);
                    return (
                        <TableCellItem>
                            <Select
                                mode="multiple"
                                onChange={(value: string[]) => onChange(record.id, value, originals)}
                                defaultValue={currentRole}
                                className={styles.select}
                                options={options}
                            />
                        </TableCellItem>
                    );
                } else {
                    return (
                        <TableCellItem
                            text={roles.map((role: GlobalRoleAssignmentContract) => role.role.name).join(',')}
                        />
                    );
                }
            },
            // ...new FilterSettings(data, (user) => (user.email !== null ? user.email : '')),
            // sorter: sorter.stringSorter((user) => user.global_roles),
            // defaultSortOrder: 'ascend',
            width: '25%',
        },
        // {
        //     title: t('Status'),
        //     dataIndex: 'lifecycle',
        //     render: (lifecycle: DataProductLifeCycleContract) => {
        //         if (lifecycle !== null) {
        //             return (
        //                 <Tag color={lifecycle.color || 'default'} className={styles.tag}>
        //                     {lifecycle.name}
        //                 </Tag>
        //             );
        //         } else {
        //             return;
        //         }
        //     },
        //     ...new FilterSettings(data, (user) => (user.lifecycle !== null ? user.lifecycle.name : '')),
        //     sorter: sorter.stringSorter((user) => (user.lifecycle !== null ? user.lifecycle.name : '')),
        //     width: '10%',
        // },
        // {
        //     title: t('Domain'),
        //     dataIndex: 'domain',
        //     render: (domain: DomainContract) => {
        //         return <TableCellItem text={domain.name} />;
        //     },
        //     ...new FilterSettings(data, (user) => user.domain.name),
        //     sorter: sorter.stringSorter((user) => user.domain.name),
        // },
        // {
        //     title: t('Type'),
        //     dataIndex: 'type',
        //     render: (type: DataProductTypeContract) => {
        //         const icon = getDataProductTypeIcon(type.icon_key);
        //         return <TableCellItem reactSVGComponent={icon} text={type.name} />;
        //     },
        //     ellipsis: true,
        //     ...new FilterSettings(data, (user) => user.type.name),
        //     sorter: sorter.stringSorter((user) => user.type.name),
        // },
        // {
        //     title: t('Access'),
        //     dataIndex: 'user_count',
        //     render: (userCount: number) => {
        //         return <TableCellItem icon={<TeamOutlined />} text={t('{{count}} users', { count: userCount })} />;
        //     },
        //     sorter: sorter.numberSorter((user) => user.user_count),
        // },
        // {
        //     title: t('Consumes'),
        //     dataIndex: 'dataset_count',
        //     render: (datasetCount: number) => {
        //         return <TableCellItem text={t('{{count}} datasets', { count: datasetCount })} />;
        //     },
        //     sorter: sorter.numberSorter((user) => user.dataset_count),
        // },
        // {
        //     title: t('Produces'),
        //     dataIndex: 'data_outputs_count',
        //     render: (dataOutputCount: number) => {
        //         return <TableCellItem text={t('{{count}} data outputs', { count: dataOutputCount })} />;
        //     },
        // },
    ];
};
