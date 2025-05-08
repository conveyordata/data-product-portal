import { PaginationConfig } from 'antd/es/pagination';

export interface ListPaginationConfig extends PaginationConfig {
    current: number;
    pageSize: number;
}
