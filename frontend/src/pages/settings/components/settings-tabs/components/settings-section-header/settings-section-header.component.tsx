import { Flex, Typography } from 'antd';
import type { ReactNode } from 'react';

type Props = {
    title: string;
    description: string;
    extra?: ReactNode;
};

export function SettingsSectionHeader({ title, description, extra }: Props) {
    return (
        <Flex justify="space-between" align="center">
            <Flex vertical>
                <Typography.Title level={3} style={{ margin: 0 }}>
                    {title}
                </Typography.Title>
                <Typography.Text type="secondary">{description}</Typography.Text>
            </Flex>
            {extra}
        </Flex>
    );
}
