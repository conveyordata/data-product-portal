import { PaginationConfig } from 'antd/es/pagination';
import { useState } from 'react';

import { DEFAULT_LIST_PAGINATION } from '@/constants/list.constants';

type Props = {
    initialPagination?: PaginationConfig;
};

export const useListPagination = ({ initialPagination = DEFAULT_LIST_PAGINATION }: Props) => {
    const [pagination, setPagination] = useState<PaginationConfig>(initialPagination);

    const resetPagination = () => {
        setPagination(initialPagination);
    };

    const handleTotalChange = (total: number) => {
        setPagination((prev) => ({
            ...prev,
            total,
        }));
    };

    const handleCurrentPageChange = (current: number) => {
        setPagination((prev) => ({
            ...prev,
            current,
        }));
    };

    const handlePageSizeChange = (pageSize: number) => {
        setPagination((prev) => ({
            ...prev,
            pageSize,
        }));
    };

    const handlePaginationChange = (pagination: PaginationConfig) => {
        setPagination(pagination);
    };
    return {
        pagination,
        resetPagination,
        handleTotalChange,
        handlePageSizeChange,
        handleCurrentPageChange,
        handlePaginationChange,
    };
};
