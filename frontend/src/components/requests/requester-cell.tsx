import { Avatar, Space, Typography, theme } from 'antd';

type Props = {
    name: string;
    email: string;
};

export function RequesterCell({ name, email }: Props) {
    const { useToken } = theme;
    const { token } = useToken();

    const secondaryColor = token.colorPrimary;
    const initials = name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase();

    return (
        <Space size="small">
            <Avatar style={{ backgroundColor: secondaryColor }}>{initials}</Avatar>
            <div>
                <div>{name}</div>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    {email}
                </Typography.Text>
            </div>
        </Space>
    );
}
