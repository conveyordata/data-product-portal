import { TablePaginationConfig } from '@/types/shared/tables.ts';

export const DEFAULT_TABLE_PAGINATION: TablePaginationConfig = {
    current: 1,
    pageSize: 10,
    total: 0,
};

export const TABLE_SUBSECTION_PAGINATION: TablePaginationConfig = {
    current: 1,
    pageSize: 5,
    total: 0,
};
