import { TeamOutlined } from '@ant-design/icons';
import { Button, Checkbox, Flex, Input, type TableColumnsType, Typography } from 'antd';
import { useMemo, useState } from 'react';
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

const IDENTITY_TYPES: Identity['type'][] = ['user', 'group', 'machine_user'];

type Props = {
    onSelect: (identity: Identity) => void;
    identityIdsToHide?: string[];
    disabled?: boolean;
};

export function IdentitySelector({ onSelect, identityIdsToHide, disabled = false }: Props) {
    const { t } = useTranslation();
    const identitiesQuery = useIdentities();
    const [searchTerm, setSearchTerm] = useState('');
    const [identityTypes, setIdentityTypes] = useState(IDENTITY_TYPES);
    const filteredIdentities = useMemo(() => {
        const hiddenIds = new Set(identityIdsToHide);
        return (identitiesQuery.currentData ?? [])
            .filter(
                (identity) =>
                    !hiddenIds.has(identity.id) &&
                    identityTypes.includes(identity.type) &&
                    identityMatchesSearch(identity, searchTerm),
            )
            .sort((left, right) => getIdentityDisplayName(left).localeCompare(getIdentityDisplayName(right)));
    }, [identitiesQuery.currentData, identityIdsToHide, identityTypes, searchTerm]);
    const { pagination, handlePaginationChange, handleCurrentPageChange } = useTablePagination(filteredIdentities);

    const columns: TableColumnsType<Identity> = [
        {
            key: 'name',
            title: t('Name'),
            render: (_, identity) => (
                <Flex vertical>
                    <Typography.Text ellipsis={{ tooltip: getIdentityDisplayName(identity) }}>
                        {getIdentityDisplayName(identity)}
                    </Typography.Text>
                    <Typography.Text type="secondary" ellipsis={{ tooltip: getIdentitySecondaryLabel(identity) }}>
                        {getIdentitySecondaryLabel(identity)}
                    </Typography.Text>
                </Flex>
            ),
        },
        {
            key: 'type',
            title: t('Type'),
            width: '25%',
            render: (_, identity) => <Typography.Text>{getIdentityTypeLabel(identity, t)}</Typography.Text>,
        },
        {
            key: 'action',
            title: t('Actions'),
            width: '20%',
            render: (_, identity) => (
                <Button
                    type="link"
                    size="small"
                    disabled={disabled || identitiesQuery.isFetching}
                    aria-label={t('Select {{name}} ({{type}})', {
                        name: getIdentityDisplayName(identity),
                        type: getIdentityTypeLabel(identity, t),
                    })}
                    onClick={() => onSelect(identity)}
                >
                    {t('Select')}
                </Button>
            ),
        },
    ];

    return (
        <Flex vertical gap="middle">
            <Input.Search
                type="search"
                aria-label={t('Search identities')}
                placeholder={t('Search by name, email, or external ID')}
                allowClear
                disabled={disabled}
                value={searchTerm}
                onChange={(event) => {
                    setSearchTerm(event.target.value);
                    handleCurrentPageChange(1);
                }}
            />
            <Checkbox.Group<Identity['type']>
                aria-label={t('Identity types')}
                disabled={disabled}
                options={[
                    { label: t('Users'), value: 'user' },
                    { label: t('Groups'), value: 'group' },
                    { label: t('Machine Users'), value: 'machine_user' },
                ]}
                value={identityTypes}
                onChange={(types) => {
                    setIdentityTypes(types);
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
                    hasOtherFilters: identityTypes.length !== IDENTITY_TYPES.length,
                    onClear: () => {
                        setSearchTerm('');
                        setIdentityTypes(IDENTITY_TYPES);
                        handleCurrentPageChange(1);
                    },
                }}
                pagination={{
                    ...pagination,
                    total: filteredIdentities.length,
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
                rowKey="id"
                size="small"
                tableLayout="fixed"
            />
        </Flex>
    );
}
