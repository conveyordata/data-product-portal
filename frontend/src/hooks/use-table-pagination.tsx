import { useCallback, useEffect, useState } from 'react';

import { DEFAULT_TABLE_PAGINATION } from '@/constants/table.constants.ts';
import type { PaginationProps } from 'antd/es/pagination/Pagination';

const defaultValues: Props = {
    initialPagination: DEFAULT_TABLE_PAGINATION,
};

type Props = {
    initialPagination: PaginationProps;
};
export const useTablePagination = (elements: object[], props: Partial<Props> = {}) => {
    const config = { ...defaultValues, ...props };
    const [pagination, setPagination] = useState<PaginationProps>(config.initialPagination);

    const resetPagination = useCallback(() => {
        setPagination(config.initialPagination);
    }, [config.initialPagination]);

    const handleTotalChange = useCallback((total: number) => {
        setPagination((prev) =>
            prev.total === total
                ? prev
                : {
                      ...prev,
                      total,
                  },
        );
    }, []);

    const handleCurrentPageChange = useCallback((current: number) => {
        setPagination((prev) =>
            prev.current === current
                ? prev
                : {
                      ...prev,
                      current,
                  },
        );
    }, []);

    const handlePageSizeChange = useCallback((pageSize: number) => {
        setPagination((prev) =>
            prev.pageSize === pageSize
                ? prev
                : {
                      ...prev,
                      pageSize,
                  },
        );
    }, []);

    const handlePaginationChange = (pagination: PaginationProps) => {
        setPagination(pagination);
    };

    useEffect(() => {
        if (elements.length !== pagination.total) {
            handleTotalChange(elements.length);

            if (pagination.current && pagination.current > elements.length) {
                handleCurrentPageChange(elements.length);
            }
        }
    }, [elements, pagination, handleTotalChange, handleCurrentPageChange]);

    return {
        pagination,
        resetPagination,
        handleTotalChange,
        handleCurrentPageChange,
        handlePageSizeChange,
        handlePaginationChange,
    };
};
