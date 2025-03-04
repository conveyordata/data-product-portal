import { Avatar, Flex, Typography } from 'antd';
import type { ComponentProps } from 'react';

import styles from './user-avatar.module.scss';

const { Text, Link } = Typography;

type Props = {
    name: string;
    email: string;
    color?: string;
    linkProps?: ComponentProps<typeof Link>;
    textProps?: ComponentProps<typeof Text>;
};

export function UserAvatar({ name, email, color, linkProps, textProps }: Props) {
    return (
        <Flex className={styles.userAvatarContainer}>
            <Avatar className={styles.avatar} style={{ background: color }}>
                {name.split('')[0].toUpperCase()}
            </Avatar>
            <Flex vertical className={styles.userInfo}>
                <Text strong {...textProps}>
                    {name}
                </Text>
                <Link {...linkProps}>{email}</Link>
            </Flex>
        </Flex>
    );
}
