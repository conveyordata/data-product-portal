import { BarChartOutlined } from '@ant-design/icons';
import { Card, Flex } from 'antd';
import type { ReactNode } from 'react';

import { EmptyState } from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';

type ChartCardProps = {
    title: string;
    isLoading: boolean;
    hasData: boolean;
    emptyTitle: string;
    emptyDescription: string;
    children: ReactNode;
};

export function ChartCard({ title, isLoading, hasData, emptyTitle, emptyDescription, children }: ChartCardProps) {
    return (
        <Card title={title}>
            {isLoading ? (
                <LoadingSpinner />
            ) : !hasData ? (
                <Flex align="center" justify="center">
                    <EmptyState icon={<BarChartOutlined />} title={emptyTitle} description={emptyDescription} />
                </Flex>
            ) : (
                children
            )}
        </Card>
    );
}
