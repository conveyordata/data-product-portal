import { InboxOutlined } from '@ant-design/icons';
import { Flex, Input, Radio, Tooltip } from 'antd';
import { parseAsBoolean, parseAsString, useQueryState } from 'nuqs';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useTableColumns } from '@/pages/product-studio/components/my-requests-tab/use-table-columns.tsx';
import { type TableRow, transformToTableRow } from '@/pages/product-studio/components/requests/request-utils.ts';
import { filterBySearch } from '@/pages/product-studio/components/requests/requests-search.ts';
import { useGetUserRequestsQuery } from '@/store/api/services/generated/usersApi.ts';

export function MyRequestsTab() {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));
    const [filterOutOldInactiveRequests, setFilterOutOldInactiveRequests] = useQueryState(
        'filterOutOldInactiveRequests',
        parseAsBoolean.withDefault(true),
    );
    const requestsQuery = useGetUserRequestsQuery(filterOutOldInactiveRequests);
    const { data: { my_requests: myRequests = [] } = {} } = requestsQuery;
    const { pagination, handlePaginationChange } = useTablePagination([]);

    const tableData: TableRow[] = useMemo(() => {
        return filterBySearch(myRequests, searchTerm).map(transformToTableRow);
    }, [myRequests, searchTerm]);

    const columns = useTableColumns();

    return (
        <Flex vertical gap="small">
            <Flex gap="small" align="center">
                <Input.Search
                    placeholder={t('Search requests...')}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{ maxWidth: 400 }}
                    allowClear
                />
                <Radio.Group
                    value={filterOutOldInactiveRequests}
                    onChange={(e) => setFilterOutOldInactiveRequests(e.target.value)}
                    optionType="button"
                >
                    <Radio.Button value={true}>
                        <Tooltip
                            title={t(
                                'Active requests are either pending requests, or requests approved/denied over the last 30 days',
                            )}
                        >
                            {t('Active requests')}
                        </Tooltip>
                    </Radio.Button>
                    <Radio.Button value={false}>{t('All requests')}</Radio.Button>
                </Radio.Group>
            </Flex>
            <ListTable
                query={requestsQuery}
                dataSource={tableData}
                columns={columns}
                subject={t('requests')}
                emptyState={{
                    icon: <InboxOutlined />,
                    title: t('No requests yet'),
                    description: t(
                        'Access you request to Output Ports appears here, together with the decision on it.',
                    ),
                }}
                filter={{
                    hasOtherFilters: filterOutOldInactiveRequests,
                    searchTerm,
                    onClear: () => {
                        setSearchTerm(null);
                        setFilterOutOldInactiveRequests(false);
                    },
                }}
                size="small"
                pagination={{
                    ...pagination,
                    onChange: (page, pageSize) => {
                        handlePaginationChange({ current: page, pageSize });
                    },
                }}
            />
        </Flex>
    );
}
