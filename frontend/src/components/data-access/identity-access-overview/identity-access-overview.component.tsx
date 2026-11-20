import { Flex, Typography } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { IdentityAvatarWithDetails } from '@/components/identity-avatar/identity-avatar.component.tsx';
import { compareIdentities, type Identity } from '@/utils/identity.ts';
import styles from './identity-access-overview.module.scss';

type Props = {
    identities?: Identity[];
    title: ReactNode;
};

export function IdentityAccessOverview({ identities, title }: Props) {
    const sorted = useMemo(() => [...(identities ?? [])].sort(compareIdentities), [identities]);

    return (
        <Flex vertical className={styles.container}>
            <Flex vertical className={styles.sectionWrapper}>
                <Typography.Title level={5}>{title}</Typography.Title>
                <Flex vertical className={styles.identityAvatarList}>
                    {sorted.map((identity) => (
                        <IdentityAvatarWithDetails key={identity.id} identity={identity} />
                    ))}
                </Flex>
            </Flex>
        </Flex>
    );
}
