import styles from './loading-spinner.module.scss';
import { Flex, Spin, SpinProps } from 'antd';
import { ReactNode } from 'react';

type Props = {
    children?: ReactNode;
    size?: 'small' | 'default' | 'large';
    spinProps?: SpinProps;
};

export function LoadingSpinner({ children, size = 'large', spinProps }: Props) {
    return (
        <Flex className={styles.loadingContainer}>
            <Spin size={size} className={styles.loading} {...spinProps}>
                {children || null}
            </Spin>
        </Flex>
    );
}
