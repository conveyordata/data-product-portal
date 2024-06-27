import { Flex, theme, Typography } from 'antd';
import styles from './user-access-overview.module.scss';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { UserContract } from '@/types/users';
import { ReactNode } from 'react';

const { useToken } = theme;

type Props = {
    users: UserContract[];
    title?: ReactNode;
};

export function UserAccessOverview({ users = [], title }: Props) {
    const { token } = useToken();
    return (
        <Flex vertical className={styles.container}>
            <Flex vertical className={styles.sectionWrapper}>
                <Typography.Title level={5}>{title}</Typography.Title>

                {/*  user avatar */}
                <Flex vertical className={styles.userAvatarList}>
                    {users.map((user) => (
                        <UserAvatar
                            key={user.id}
                            name={`${user.first_name} ${user.last_name}`}
                            email={user.email}
                            color={token.colorPrimary}
                        />
                    ))}
                </Flex>
            </Flex>
        </Flex>
    );
}
