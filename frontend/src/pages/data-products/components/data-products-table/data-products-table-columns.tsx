import { CrownOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Badge, Popover, type TableColumnsType, Tag, Tooltip } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { DataProductStatus, DataProductsGetContract } from '@/types/data-product';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import type { DataProductTypeContract } from '@/types/data-product-type';
import type { DomainContract } from '@/types/domain';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

import styles from './data-products-table.module.scss';

const iconColumnWidth = 30;

function renderTeamCell(
    team: { user: { id: string; first_name: string; last_name: string; email: string }; role: { name: string } }[],
    t: TFunction,
) {
    if (!team || team.length === 0) return null;

    // Group users by role
    const grouped: Record<string, { role: string; users: typeof team }> = {};
    team.forEach((member) => {
        const role = member.role.name;
        if (!grouped[role]) {
            grouped[role] = { role, users: [] };
        }
        grouped[role].users.push(member);
    });
    // Sort roles: owners first, then alphabetically
    const sortedRoles = Object.keys(grouped).sort((a, b) => {
        if (a.toLowerCase() === 'owner') return -1;
        if (b.toLowerCase() === 'owner') return 1;
        return a.localeCompare(b);
    });

    return (
        <div className={styles.teamCell}>
            {sortedRoles.map((role) => {
                const users = grouped[role].users;
                const showUsers = users.slice(0, 2);
                const extraCount = users.length - showUsers.length;
                const isOwner = role.toLowerCase() === 'owner';
                const roleIcon = isOwner ? (
                    <CrownOutlined style={{ marginRight: 4 }} />
                ) : (
                    <UserOutlined style={{ marginRight: 4 }} />
                );
                return (
                    <div key={role} className={styles.teamRoleGroup}>
                        <span className={styles.teamRoleLabel}>
                            {roleIcon}
                            {role}
                        </span>
                        <span className={styles.teamAvatars}>
                            {showUsers.map((member) => (
                                <Tooltip
                                    key={member.user.id}
                                    title={`${member.user.first_name} ${member.user.last_name} ${member.user.email}`}
                                >
                                    <Avatar size="small" className={styles.avatar}>
                                        {member.user.first_name.split('')[0].toUpperCase()}
                                        {member.user.last_name.split('')[0].toUpperCase()}
                                    </Avatar>
                                </Tooltip>
                            ))}
                            {extraCount > 0 && (
                                <span className={styles.teamMore}>
                                    +{extraCount} {t('more')}
                                </span>
                            )}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}

export const getDataProductTableColumns = ({
    t,
    dataProducts: data,
}: {
    t: TFunction;
    dataProducts: DataProductsGetContract;
}): TableColumnsType<DataProductsGetContract[0]> => {
    const sorter = new Sorter<DataProductsGetContract[0]>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        // This is an empty column to match to give a small indentation to the table and match the datasets table icon column
        {
            title: undefined,
            dataIndex: 'status',
            width: iconColumnWidth,
            render: (status: DataProductStatus) => {
                return (
                    <Popover content={getStatusLabel(t, status)} placement={'top'}>
                        <TableCellItem icon={<Badge status={getBadgeStatus(status)} />} />
                    </Popover>
                );
            },
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: {
                showTitle: false,
            },
            render: (name) => {
                return <TableCellItem text={name} tooltip={{ content: name }} />;
            },
            sorter: sorter.stringSorter((dp) => dp.name),
            defaultSortOrder: 'ascend',
            width: '25%',
        },
        {
            title: t('Status'),
            dataIndex: 'lifecycle',
            render: (lifecycle: DataProductLifeCycleContract) => {
                if (lifecycle !== null) {
                    return (
                        <Tag color={lifecycle.color || 'default'} className={styles.tag}>
                            {lifecycle.name}
                        </Tag>
                    );
                }
                return;
            },
            ...new FilterSettings(data, (dp) => (dp.lifecycle !== null ? dp.lifecycle.name : '')),
            sorter: sorter.stringSorter((dp) => (dp.lifecycle !== null ? dp.lifecycle.name : '')),
            width: '10%',
        },
        {
            title: t('Domain'),
            dataIndex: 'domain',
            render: (domain: DomainContract) => {
                return <TableCellItem text={domain.name} />;
            },
            ...new FilterSettings(data, (dp) => dp.domain.name),
            sorter: sorter.stringSorter((dp) => dp.domain.name),
        },
        {
            title: t('Type'),
            dataIndex: 'type',
            render: (type: DataProductTypeContract) => {
                const icon = getDataProductTypeIcon(type.icon_key);
                return <TableCellItem reactSVGComponent={icon} text={type.name} />;
            },
            ellipsis: true,
            ...new FilterSettings(data, (dp) => dp.type.name),
            sorter: sorter.stringSorter((dp) => dp.type.name),
        },
        {
            title: t('Access'),
            dataIndex: 'user_count',
            render: (userCount: number) => {
                return <TableCellItem icon={<TeamOutlined />} text={t('{{count}} users', { count: userCount })} />;
            },
            sorter: sorter.numberSorter((dp) => dp.user_count),
        },
        {
            title: t('Consumes'),
            dataIndex: 'dataset_count',
            render: (datasetCount: number) => {
                return <TableCellItem text={t('{{count}} datasets', { count: datasetCount })} />;
            },
            sorter: sorter.numberSorter((dp) => dp.dataset_count),
        },
        {
            title: t('Produces'),
            dataIndex: 'data_outputs_count',
            render: (dataOutputCount: number) => {
                return <TableCellItem text={t('{{count}} data outputs', { count: dataOutputCount })} />;
            },
        },
        {
            title: t('Team'),
            dataIndex: 'assignments',
            render: (assignments) => renderTeamCell(assignments, t),
            width: 180,
        },
    ];
};
