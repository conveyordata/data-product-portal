import { useState } from 'react';

import { DEFAULT_LIST_PAGINATION } from '@/constants/list.constants';
import { ListPaginationConfig } from '@/types/shared/lists';

type Props = {
    initialPagination?: ListPaginationConfig;
};

export const useListPagination = ({ initialPagination = DEFAULT_LIST_PAGINATION }: Props) => {
    const [pagination, setPagination] = useState<ListPaginationConfig>(initialPagination);

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

    const handlePaginationChange = (pagination: ListPaginationConfig) => {
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
