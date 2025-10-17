import type { TablePaginationConfig } from '@/types/shared/tables.ts';

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

export const HISTORY_PAGINATION: TablePaginationConfig = {
    current: 1,
    pageSize: 7,
    total: 0,
};

export const DATA_OUTPUTS_TABLE_PAGINATION: TablePaginationConfig = {
    current: 1,
    pageSize: 4,
    total: 0,
};
