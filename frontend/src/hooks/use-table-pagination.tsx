import { useState } from 'react';
import type { TablePaginationConfig } from 'antd';
import { DEFAULT_TABLE_PAGINATION } from '@/constants/table.constants.ts';

type Props = {
    initialPagination?: TablePaginationConfig;
};
export const useTablePagination = ({ initialPagination = DEFAULT_TABLE_PAGINATION }: Props) => {
    const [pagination, setPagination] = useState<TablePaginationConfig>(initialPagination);

    const resetPagination = () => {
        setPagination(initialPagination);
    };

    const handleTotalChange = (total: number) => {
        setPagination((prev) =>
            prev.total === total
                ? prev
                : {
                      ...prev,
                      total,
                  },
        );
    };

    const handleCurrentPageChange = (current: number) => {
        setPagination((prev) =>
            prev.current === current
                ? prev
                : {
                      ...prev,
                      current,
                  },
        );
    };

    const handlePageSizeChange = (pageSize: number) => {
        setPagination((prev) =>
            prev.pageSize === pageSize
                ? prev
                : {
                      ...prev,
                      pageSize,
                  },
        );
    };

    const handlePaginationChange = (pagination: TablePaginationConfig) => {
        setPagination(pagination);
    };

    return {
        pagination,
        resetPagination,
        handleTotalChange,
        handleCurrentPageChange,
        handlePageSizeChange,
        handlePaginationChange,
    };
};
