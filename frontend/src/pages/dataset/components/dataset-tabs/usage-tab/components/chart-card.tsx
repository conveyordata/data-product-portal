import { Card, Empty, Flex } from 'antd';
import type { ReactNode } from 'react';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import styles from './chart-card.module.scss';

type ChartCardProps = {
    title: string;
    isLoading: boolean;
    hasData: boolean;
    emptyDescription: string;
    children: ReactNode;
};

export function ChartCard({ title, isLoading, hasData, emptyDescription, children }: ChartCardProps) {
    let content: ReactNode = children;

    if (isLoading) {
        content = (
            <Flex align="center" justify="center" className={styles.content}>
                <LoadingSpinner />
            </Flex>
        );
    } else if (!hasData) {
        content = (
            <Flex align="center" justify="center" className={styles.content}>
                <Empty description={emptyDescription} />
            </Flex>
        );
    }

    return <Card title={title}>{content}</Card>;
}
