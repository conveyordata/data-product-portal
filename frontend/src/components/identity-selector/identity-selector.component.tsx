import { TeamOutlined } from '@ant-design/icons';
import { Col, Flex, Input, Row, type TableColumnsType, type TableProps, Typography } from 'antd';
import { type ReactNode, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { IdentityAvatarWithDetails } from '@/components/identity-avatar/identity-avatar.component.tsx';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { useIdentities } from '@/hooks/use-identities.ts';
import {
    getIdentityDisplayName,
    getIdentityTypeLabel,
    type Identity,
    identityMatchesSearch,
} from '@/utils/identity.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

const compareNames = new Sorter<Identity>().stringSorter(getIdentityDisplayName);

type Props = {
    renderAction?: (identity: Identity, disabled: boolean) => ReactNode;
    actionTitle?: ReactNode;
    identityIdsToHide?: string[];
    disabled?: boolean;
    columns?: (identities: Identity[], disabled: boolean) => TableColumnsType<Identity>;
    search?: { value: string; onChange: (value: string) => void; span: number };
    tableProps?: Pick<TableProps<Identity>, 'tableLayout' | 'scroll' | 'rowClassName' | 'rowHoverable'>;
};

export function IdentitySelector({
    renderAction,
    actionTitle,
    identityIdsToHide,
    disabled = false,
    columns: buildColumns,
    search,
    tableProps,
}: Props) {
    const { t } = useTranslation();
    const identitiesQuery = useIdentities();
    const actionsDisabled = disabled || identitiesQuery.isFetching;
    const [localSearchTerm, setLocalSearchTerm] = useState('');
    const searchTerm = search?.value ?? localSearchTerm;
    const setSearchTerm = search?.onChange ?? setLocalSearchTerm;
    const filteredIdentities = useMemo(() => {
        const hiddenIds = new Set(identityIdsToHide);
        return (identitiesQuery.currentData ?? []).filter(
            (identity) => !hiddenIds.has(identity.id) && identityMatchesSearch(identity, searchTerm),
        );
    }, [identitiesQuery.currentData, identityIdsToHide, searchTerm]);

    const columns: TableColumnsType<Identity> = [
        {
            key: 'name',
            title: t('Name'),
            sorter: { compare: compareNames, multiple: 1 },
            defaultSortOrder: 'ascend',
            sortDirections: ['ascend', 'descend', 'ascend'],
            render: (_, identity) => <IdentityAvatarWithDetails identity={identity} />,
        },
        {
            key: 'type',
            title: t('Type'),
            width: '20%',
            ...new FilterSettings(identitiesQuery.currentData ?? [], (identity) => getIdentityTypeLabel(identity, t)),
            sorter: {
                compare: (left, right) => getIdentityTypeLabel(left, t).localeCompare(getIdentityTypeLabel(right, t)),
                multiple: 2,
            },
            render: (_, identity) => <Typography.Text>{getIdentityTypeLabel(identity, t)}</Typography.Text>,
        },
    ];
    if (renderAction) {
        columns.push({
            key: 'action',
            title: actionTitle,
            width: '25%',
            render: (_, identity) => renderAction(identity, actionsDisabled),
        });
    }

    return (
        <Flex vertical gap="middle">
            <Row gutter={16}>
                <Col span={search?.span ?? 24}>
                    <Input.Search
                        type="search"
                        data-cy="identity-selector-search"
                        aria-label={t('Search identities')}
                        placeholder={t('Search by name, email, or external ID')}
                        allowClear
                        disabled={disabled}
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.target.value)}
                    />
                </Col>
            </Row>
            <ListTable<Identity>
                query={identitiesQuery}
                dataSource={filteredIdentities}
                columns={buildColumns ? buildColumns(filteredIdentities, actionsDisabled) : columns}
                subject={t('identities')}
                emptyState={{
                    icon: <TeamOutlined />,
                    title: t('No identities available'),
                    description: t('There are no users, groups, or machine users available to select.'),
                    size: 'small',
                }}
                filter={{
                    searchTerm,
                    onClear: () => setSearchTerm(''),
                }}
                pagination={{
                    placement: ['bottomEnd'],
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
                rowKey="id"
                size="small"
                tableLayout="fixed"
                scroll={{ x: 560 }}
                {...tableProps}
            />
        </Flex>
    );
}
