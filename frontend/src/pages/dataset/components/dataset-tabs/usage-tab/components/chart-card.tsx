import { Card, Empty, Flex, Spin } from 'antd';
import clsx from 'clsx';
import type { ReactNode } from 'react';

import styles from './chart-card.module.scss';

type ChartCardProps = {
    title: string;
    className?: string;
    isLoading: boolean;
    hasData: boolean;
    emptyDescription: string;
    children: ReactNode;
};

export function ChartCard({ title, className, isLoading, hasData, emptyDescription, children }: ChartCardProps) {
    let content: ReactNode = children;
    const cardClassName = clsx(styles.chartCard, className);

    if (isLoading) {
        content = (
            <Flex align="center" justify="center" className={styles.content}>
                <Spin size="large" />
            </Flex>
        );
    } else if (!hasData) {
        content = (
            <Flex align="center" justify="center" className={styles.content}>
                <Empty description={emptyDescription} />
            </Flex>
        );
    }

    return (
        <Card className={cardClassName} title={title}>
            {content}
        </Card>
    );
}
