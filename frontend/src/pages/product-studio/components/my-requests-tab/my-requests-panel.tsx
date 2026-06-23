import { Flex, Input, Table } from 'antd';
import { parseAsString, useQueryState } from 'nuqs';
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
    const { data: { my_requests: myRequests = [] } = {}, isFetching } = useGetUserRequestsQuery();
    const { pagination, handlePaginationChange } = useTablePagination([]);

    const tableData: TableRow[] = useMemo(() => {
        return filterBySearch(myRequests, searchTerm).map(transformToTableRow);
    }, [myRequests, searchTerm]);

    const columns = useTableColumns();

    return (
        <Flex vertical gap="small">
            <Input.Search
                placeholder={t('Search requests...')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ maxWidth: 400 }}
                allowClear
            />
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
