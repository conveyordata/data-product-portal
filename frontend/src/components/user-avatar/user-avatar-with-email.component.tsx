import { Flex, Typography } from 'antd';
import type { UserContract } from '@/types/users';
import { UserAvatar } from './user-avatar.component';
import styles from './user-avatar.module.scss';

type Props = {
    user: UserContract;
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
