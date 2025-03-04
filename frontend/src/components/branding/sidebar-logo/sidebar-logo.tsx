import { Flex, Typography } from 'antd';
import clsx from 'clsx';

import { useGetGeneralSettingsQuery } from '@/store/features/general-settings/general-settings-api-slice';

import styles from './sidebar-logo.module.scss';

type Props = {
    variant?: 'light' | 'dark';
};

export function SidebarLogo({ variant = 'light' }: Props) {
    const { data: settings } = useGetGeneralSettingsQuery();
    return (
        <Flex vertical className={styles.logoWrapper}>
            <Typography.Text className={clsx(styles.logoText, styles[variant])}>
                {settings?.portal_name}
            </Typography.Text>
        </Flex>
    );
}
