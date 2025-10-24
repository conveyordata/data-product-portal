import { Avatar, Flex, Typography } from 'antd';

import styles from './user-avatar.module.scss';

type Props = {
    name: string;
    email: string;
    color: string;
    size?: 'small' | 'default' | 'large';
};

export function UserAvatar({ name, email, color, size = 'default' }: Props) {
    return (
        <Flex align="center" className={styles.userAvatarContainer}>
            <Avatar size={size} className={styles.avatar} style={{ backgroundColor: color }}>
                {name.charAt(0)}
            </Avatar>
            <Flex vertical>
                <Typography.Text strong>{name}</Typography.Text>
                <Typography.Text type="secondary" className={styles.email}>
                    {email}
                </Typography.Text>
            </Flex>
        </Flex>
    );
}
