import { Card, Empty, Flex } from 'antd';
import type { ReactNode } from 'react';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';

type ChartCardProps = {
    title: string;
    isLoading: boolean;
    hasData: boolean;
    emptyDescription: string;
    children: ReactNode;
};

export function ChartCard({ title, isLoading, hasData, emptyDescription, children }: ChartCardProps) {
    return (
        <Card title={title}>
            {isLoading ? (
                <LoadingSpinner />
            ) : !hasData ? (
                <Flex align="center" justify="center">
                    <Empty description={emptyDescription} />
                </Flex>
            ) : (
                children
            )}
        </Card>
    );
}
