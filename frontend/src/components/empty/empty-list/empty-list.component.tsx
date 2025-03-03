import { Empty, EmptyProps, Flex, FlexProps } from 'antd';

import styles from './empty-list.module.scss';

type Props = EmptyProps & {
    description?: string;
    containerProps?: FlexProps;
};

export function EmptyList({ description, containerProps, ...emptyProps }: Props) {
    return (
        <Flex className={styles.emptyContainer} {...containerProps}>
            <Empty {...emptyProps} description={description} />
        </Flex>
    );
}
