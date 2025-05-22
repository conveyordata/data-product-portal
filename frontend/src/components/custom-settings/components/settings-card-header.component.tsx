import { SyncOutlined } from '@ant-design/icons';
import { Button, Flex, Space, Typography } from 'antd';

type Props = {
    isDefault: boolean;
    resetToDefault: () => void;
};

export function SettingsCardHeader({ isDefault, resetToDefault }: Props) {
    if (isDefault) {
        return (
            <Space>
                <SyncOutlined />
                <Typography.Text type="secondary">{'Synced with default'}</Typography.Text>
            </Space>
        );
    } else {
        return (
            <Flex justify="space-between">
                <Typography.Text type="secondary">{'Custom Value'}</Typography.Text>
                <Button type="link" onClick={resetToDefault}>
                    {'Reset to default'}
                </Button>
            </Flex>
        );
    }
}
