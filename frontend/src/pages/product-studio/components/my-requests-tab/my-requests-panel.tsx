import { Flex, Input, Radio, Table, Tooltip } from 'antd';
import { parseAsBoolean, parseAsString, useQueryState } from 'nuqs';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
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
    const { data: { my_requests: myRequests = [] } = {}, isFetching } =
        useGetUserRequestsQuery(filterOutOldInactiveRequests);
    const { pagination, handlePaginationChange } = useTablePagination([]);

    const tableData: TableRow[] = useMemo(() => {
        return filterBySearch(myRequests, searchTerm).map(transformToTableRow);
    }, [myRequests, searchTerm]);

    const columns = useTableColumns();

    return (
        <Flex vertical gap="small">
            <Flex gap={'small'} align="center">
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
            <Table
                columns={columns}
                loading={isFetching}
                dataSource={tableData}
                size="small"
                pagination={{
                    ...pagination,
                    onChange: (page, pageSize) => {
                        handlePaginationChange({ current: page, pageSize });
                    },
                }}
                locale={{
                    emptyText: t('No requests.'),
                }}
            />
        </Flex>
    );
}
