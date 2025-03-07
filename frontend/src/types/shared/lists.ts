import { GetProp, ListProps } from 'antd';

export type ListPaginationConfig = Exclude<GetProp<ListProps<unknown>, 'pagination'>, boolean>;
