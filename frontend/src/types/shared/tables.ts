import type { GetProp, TableProps } from 'antd';

export type TablePaginationConfig = Exclude<GetProp<TableProps, 'pagination'>, boolean>;
