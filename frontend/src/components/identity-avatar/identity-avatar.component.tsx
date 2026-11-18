import { RobotOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Flex, Tooltip, Typography, theme } from 'antd';
import { useTranslation } from 'react-i18next';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import {
    getIdentityDisplayName,
    getIdentitySecondaryLabel,
    getIdentityTypeLabel,
    type Identity,
} from '@/utils/identity.ts';

export function IdentityIcon({ type }: { type: Identity['type'] }) {
    switch (type) {
        case 'user':
            return <UserOutlined />;
        case 'group':
            return <TeamOutlined />;
        case 'machine_user':
            return <RobotOutlined />;
    }
}

export function IdentityAvatarWithDetails({ identity }: { identity: Identity }) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const name = getIdentityDisplayName(identity);
    const secondaryLabel = getIdentitySecondaryLabel(identity);

    return (
        <Flex align="center" gap="small" style={{ minWidth: 0 }}>
            <Tooltip title={getIdentityTypeLabel(identity, t)}>
                <span>
                    {identity.type === 'user' ? (
                        <UserAvatar user={identity} color={token.colorPrimary} />
                    ) : (
                        <Avatar
                            size="large"
                            style={{ backgroundColor: token.colorPrimary }}
                            icon={<IdentityIcon type={identity.type} />}
                        />
                    )}
                </span>
            </Tooltip>
            <Flex vertical style={{ minWidth: 0 }}>
                <Typography.Text strong ellipsis={{ tooltip: name }}>
                    {name}
                </Typography.Text>
                <Typography.Text type="secondary" ellipsis={{ tooltip: secondaryLabel }}>
                    {secondaryLabel}
                </Typography.Text>
            </Flex>
        </Flex>
    );
}
