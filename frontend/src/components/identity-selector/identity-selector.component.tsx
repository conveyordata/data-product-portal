import { TeamOutlined } from '@ant-design/icons';
import { Flex, Input, type TableColumnsType, Typography } from 'antd';
import { type ReactNode, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { useIdentities } from '@/hooks/use-identities.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    getIdentityDisplayName,
    getIdentitySecondaryLabel,
    getIdentityTypeLabel,
    type Identity,
    identityMatchesSearch,
} from '@/utils/identity.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

const compareNames = new Sorter<Identity>().stringSorter(getIdentityDisplayName);

type Props = {
    renderAction?: (identity: Identity, disabled: boolean) => ReactNode;
    identityIdsToHide?: string[];
    disabled?: boolean;
};

export function IdentitySelector({ renderAction, identityIdsToHide, disabled = false }: Props) {
    const { t } = useTranslation();
    const identitiesQuery = useIdentities();
    const actionsDisabled = disabled || identitiesQuery.isFetching;
    const [searchTerm, setSearchTerm] = useState('');
    const filteredIdentities = useMemo(() => {
        const hiddenIds = new Set(identityIdsToHide);
        return (identitiesQuery.currentData ?? []).filter(
            (identity) => !hiddenIds.has(identity.id) && identityMatchesSearch(identity, searchTerm),
        );
    }, [identitiesQuery.currentData, identityIdsToHide, searchTerm]);
    const { pagination, handlePaginationChange, handleCurrentPageChange } = useTablePagination(filteredIdentities);

    const columns: TableColumnsType<Identity> = [
        {
            key: 'name',
            title: t('Name'),
            sorter: { compare: compareNames, multiple: 1 },
            defaultSortOrder: 'ascend',
            sortDirections: ['ascend', 'descend', 'ascend'],
            render: (_, identity) => (
                <Flex align="center" justify="space-between" gap="small">
                    <Flex vertical style={{ minWidth: 0, flex: 1 }}>
                        <Typography.Text ellipsis={{ tooltip: getIdentityDisplayName(identity) }}>
                            {getIdentityDisplayName(identity)}
                        </Typography.Text>
                        <Typography.Text type="secondary" ellipsis={{ tooltip: getIdentitySecondaryLabel(identity) }}>
                            {getIdentitySecondaryLabel(identity)}
                        </Typography.Text>
                    </Flex>
                    {renderAction && <div style={{ width: '40%' }}>{renderAction(identity, actionsDisabled)}</div>}
                </Flex>
            ),
        },
        {
            key: 'type',
            title: t('Type'),
            width: '25%',
            ...new FilterSettings(identitiesQuery.currentData ?? [], (identity) => getIdentityTypeLabel(identity, t)),
            sorter: {
                compare: (left, right) => getIdentityTypeLabel(left, t).localeCompare(getIdentityTypeLabel(right, t)),
                multiple: 2,
            },
            render: (_, identity) => <Typography.Text>{getIdentityTypeLabel(identity, t)}</Typography.Text>,
        },
    ];

    return (
        <Flex vertical gap="middle">
            <Input.Search
                type="search"
                aria-label={t('Search identities')}
                placeholder={t('Search by name or email')}
                allowClear
                disabled={disabled}
                value={searchTerm}
                onChange={(event) => {
                    setSearchTerm(event.target.value);
                    handleCurrentPageChange(1);
                }}
            />
            <ListTable<Identity>
                query={identitiesQuery}
                dataSource={filteredIdentities}
                columns={columns}
                subject={t('identities')}
                emptyState={{
                    icon: <TeamOutlined />,
                    title: t('No identities available'),
                    description: t('There are no users, groups, or machine users available to select.'),
                    size: 'small',
                }}
                filter={{
                    searchTerm,
                    onClear: () => {
                        setSearchTerm('');
                        handleCurrentPageChange(1);
                    },
                }}
                pagination={{
                    current: pagination.current,
                    pageSize: pagination.pageSize,
                    placement: ['topEnd'],
                    size: 'small',
                    showSizeChanger: false,
                    disabled,
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} identities', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
                onChange={handlePaginationChange}
                rowHoverable={false}
                rowKey="id"
                size="small"
                tableLayout="fixed"
                scroll={{ x: 560 }}
            />
        </Flex>
    );
}
