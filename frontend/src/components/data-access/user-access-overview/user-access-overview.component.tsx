import { Flex, Typography, theme } from 'antd';
import { type ReactNode, useMemo } from 'react';

import { UserAvatarWithEmail } from '@/components/user-avatar/user-avatar-with-email.component';
import type { UserContract } from '@/types/users/user.contract';
import { Sorter } from '@/utils/table-sorter.helper.ts';
import styles from './user-access-overview.module.scss';

const { useToken } = theme;

type Props = {
    users?: UserContract[];
    title?: ReactNode;
};

export function UserAccessOverview({ users = [], title }: Props) {
    const { token } = useToken();

    const sorted = useMemo(() => {
        const sorter = new Sorter<UserContract>();
        const compareFn = sorter.cascadedSorter(
            sorter.stringSorter((user) => user.last_name),
            sorter.stringSorter((user) => user.first_name),
        );
        return [...users].sort(compareFn);
    }, [users]);

    return (
        <Flex vertical className={styles.container}>
            <Flex vertical className={styles.sectionWrapper}>
                <Typography.Title level={5}>{title}</Typography.Title>

                {/*  user avatar */}
                <Flex vertical className={styles.userAvatarList}>
                    {sorted.map((user) => (
                        <UserAvatarWithEmail key={user.id} user={user} color={token.colorPrimary} />
                    ))}
                </Flex>
            </Flex>
        </Flex>
    );
}
