import { TeamOutlined } from '@ant-design/icons';
import { Flex, Form, Input, Select, type TableColumnsType, Typography } from 'antd';
import { useEffect, useId, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { useIdentities } from '@/hooks/use-identities.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { selectFilterOptionByLabel } from '@/utils/form.helper.ts';
import {
    getIdentityDisplayName,
    getIdentitySecondaryLabel,
    getIdentityTypeLabel,
    IDENTITY_TYPES,
    type Identity,
    identityMatchesSearch,
} from '@/utils/identity.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

const compareNames = new Sorter<Identity>().stringSorter(getIdentityDisplayName);

type Props = {
    onSelect: (identity: Identity) => void;
    identityTypes: Identity['type'][];
    onIdentityTypesChange: (types: Identity['type'][]) => void;
    identityIdsToHide?: string[];
    disabled?: boolean;
};

export function IdentitySelector({
    onSelect,
    identityTypes,
    onIdentityTypesChange,
    identityIdsToHide,
    disabled = false,
}: Props) {
    const { t } = useTranslation();
    const searchInputId = useId();
    const typeSelectId = useId();
    const identitiesQuery = useIdentities();
    const selectionDisabled = disabled || identitiesQuery.isFetching;
    const [searchTerm, setSearchTerm] = useState('');
    const filteredIdentities = useMemo(() => {
        const hiddenIds = new Set(identityIdsToHide);
        return (identitiesQuery.currentData ?? []).filter(
            (identity) =>
                !hiddenIds.has(identity.id) &&
                identityTypes.includes(identity.type) &&
                identityMatchesSearch(identity, searchTerm),
        );
    }, [identitiesQuery.currentData, identityIdsToHide, identityTypes, searchTerm]);
    const { pagination, handlePaginationChange, handleCurrentPageChange } = useTablePagination(filteredIdentities);

    // biome-ignore lint/correctness/useExhaustiveDependencies: Reset pagination when the caller changes the type filter.
    useEffect(() => {
        handleCurrentPageChange(1);
    }, [identityTypes, handleCurrentPageChange]);

    const columns: TableColumnsType<Identity> = [
        {
            key: 'name',
            title: t('Name'),
            sorter: { compare: compareNames, multiple: 1 },
            defaultSortOrder: 'ascend',
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
            sorter: {
                compare: (left, right) => getIdentityTypeLabel(left, t).localeCompare(getIdentityTypeLabel(right, t)),
                multiple: 2,
            },
            render: (_, identity) => <Typography.Text>{getIdentityTypeLabel(identity, t)}</Typography.Text>,
        },
    ];

    return (
        <Flex vertical gap="middle">
            <Flex gap="middle">
                <Form.Item
                    label={t('Identity')}
                    htmlFor={searchInputId}
                    required
                    layout="vertical"
                    style={{ flex: 1, minWidth: 0, marginBottom: 0 }}
                >
                    <Input.Search
                        id={searchInputId}
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
                </Form.Item>
                <Form.Item
                    label={t('Type')}
                    htmlFor={typeSelectId}
                    layout="vertical"
                    style={{ flex: 1, minWidth: 0, marginBottom: 0 }}
                >
                    <Select
                        id={typeSelectId}
                        mode="multiple"
                        placeholder={t('Identity types')}
                        allowClear
                        showSearch={{ filterOption: selectFilterOptionByLabel }}
                        disabled={disabled}
                        options={[
                            { label: t('Users'), value: 'user' },
                            { label: t('Groups'), value: 'group' },
                            { label: t('Machine Users'), value: 'machine_user' },
                        ]}
                        value={identityTypes}
                        onChange={onIdentityTypesChange}
                    />
                </Form.Item>
            </Flex>
            <ListTable<Identity>
                query={identitiesQuery}
                dataSource={filteredIdentities}
                columns={columns}
                sortDirections={['ascend', 'descend', 'ascend']}
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
                        onIdentityTypesChange(IDENTITY_TYPES);
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
                onRow={(identity) => ({
                    tabIndex: selectionDisabled ? -1 : 0,
                    'aria-disabled': selectionDisabled,
                    'aria-label': t('Select {{name}} ({{type}})', {
                        name: getIdentityDisplayName(identity),
                        type: getIdentityTypeLabel(identity, t),
                    }),
                    style: { cursor: selectionDisabled ? 'not-allowed' : 'pointer' },
                    onClick: selectionDisabled ? undefined : () => onSelect(identity),
                    onKeyDown: selectionDisabled
                        ? undefined
                        : (event) => {
                              if (event.key === 'Enter' || event.key === ' ') {
                                  event.preventDefault();
                                  onSelect(identity);
                              }
                          },
                })}
                rowKey="id"
                size="small"
                tableLayout="fixed"
            />
        </Flex>
    );
}
