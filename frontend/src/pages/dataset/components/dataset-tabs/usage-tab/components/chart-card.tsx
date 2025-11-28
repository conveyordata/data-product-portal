import { Card, Empty, Flex, Spin } from 'antd';
import type { ReactNode } from 'react';

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
            <Flex align="center" justify="center" style={{ minHeight: 280 }}>
                <Spin size="large" />
            </Flex>
        );
    } else if (!hasData) {
        content = (
            <Flex align="center" justify="center" style={{ minHeight: 280 }}>
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
