import { Avatar, Space, Typography } from 'antd';

type Props = {
    name: string;
    email: string;
};

export function RequesterCell({ name, email }: Props) {
    const initials = name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase();

    return (
        <Space size="small">
            <Avatar size="small" style={{ backgroundColor: '#1890ff' }}>
                {initials}
            </Avatar>
            <div>
                <div>{name}</div>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    {email}
                </Typography.Text>
            </div>
        </Space>
    );
}
