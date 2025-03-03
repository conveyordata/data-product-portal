import { Avatar, Flex, Typography, type TypographyProps } from 'antd';

import styles from './user-avatar.module.scss';

type Props = {
    name: string;
    email: string;
    color?: string;
    linkProps?: TypographyProps['Link']['defaultProps'];
    textProps?: TypographyProps['Text']['defaultProps'];
};

export function UserAvatar({ name, email, color, linkProps, textProps }: Props) {
    return (
        <Flex className={styles.userAvatarContainer}>
            <Avatar className={styles.avatar} style={{ background: color }}>
                {name.split('')[0].toUpperCase()}
            </Avatar>
            <Flex vertical className={styles.userInfo}>
                <Typography.Text strong {...textProps}>
                    {name}
                </Typography.Text>
                <Typography.Link {...linkProps}>{email}</Typography.Link>
            </Flex>
        </Flex>
    );
}
