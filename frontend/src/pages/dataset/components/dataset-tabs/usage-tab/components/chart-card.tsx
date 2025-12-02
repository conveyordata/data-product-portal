import { Card, Empty, Flex } from 'antd';
import type { ReactNode } from 'react';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';

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

    if (isLoading) {
        content = (
            <Flex align="center" justify="center">
                <LoadingSpinner />
            </Flex>
        );
    } else if (!hasData) {
        content = (
            <Flex align="center" justify="center">
                <Empty description={emptyDescription} />
            </Flex>
        );
    }

    return (
        <Card className={className} title={title} styles={{ body: { padding: 0 } }}>
            {content}
        </Card>
    );
}
