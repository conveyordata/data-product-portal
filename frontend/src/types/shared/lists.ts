import { GetProp, ListProps } from 'antd';

export type ListPaginationConfig = Exclude<GetProp<ListProps<any>, 'pagination'>, boolean>;
