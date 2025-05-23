import { Flex, theme, Typography } from 'antd';
import { type ReactNode, useMemo } from 'react';

import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import type { UserContract } from '@/types/users';

import styles from './user-access-overview.module.scss';

const { useToken } = theme;

type Props = {
    users: UserContract[];
    title?: ReactNode;
};

export function UserAccessOverview({ users = [], title }: Props) {
    const { token } = useToken();

    const sorted = useMemo(() => {
        return [...users].sort((a, b) => a.email.localeCompare(b.email));
    }, [users]);

    return (
        <Flex vertical className={styles.container}>
            <Flex vertical className={styles.sectionWrapper}>
                <Typography.Title level={5}>{title}</Typography.Title>

                {/*  user avatar */}
                <Flex vertical className={styles.userAvatarList}>
                    {sorted.map((user) => (
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
