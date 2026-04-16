import { Flex, Typography } from 'antd';
import type { User } from '@/store/api/services/generated/usersApi.ts';
import { UserAvatar } from './user-avatar.component';
import styles from './user-avatar.module.scss';

type Props = {
    user: User;
    color?: string;
    size?: 'small' | 'default' | 'large';
};

export function UserAvatarWithEmail({ user, color, size = 'default' }: Props) {
    return (
        <Flex align="center" gap="small">
            <UserAvatar user={user} color={color} size={size} />
            <Flex vertical>
                <Typography.Text strong>{`${user.first_name} ${user.last_name}`}</Typography.Text>
                <Typography.Text type="secondary" className={styles.email}>
                    {user.email}
                </Typography.Text>
            </Flex>
        </Flex>
    );
}
