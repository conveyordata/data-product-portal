import { Flex, Spin, type SpinProps } from 'antd';
import type { ReactNode } from 'react';

import styles from './loading-spinner.module.scss';

type Props = {
    children?: ReactNode;
    size?: 'small' | 'default' | 'large';
    spinProps?: SpinProps;
};

export function LoadingSpinner({ children, size = 'large', spinProps }: Props) {
    return (
        <Flex className={styles.loadingContainer} justify={'center'} align={'center'}>
            <Spin size={size} {...spinProps}>
                {children || null}
            </Spin>
        </Flex>
    );
}
