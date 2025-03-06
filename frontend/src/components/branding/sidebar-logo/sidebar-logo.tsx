import { Flex, Typography } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import { useGetThemeSettingsQuery } from '@/store/features/theme-settings/theme-settings-api-slice';

import styles from './sidebar-logo.module.scss';

type Props = {
    variant?: 'light' | 'dark';
};

export function SidebarLogo({ variant = 'light' }: Props) {
    const { t } = useTranslation();
    const { data: settings } = useGetThemeSettingsQuery();
    return (
        <Flex vertical className={styles.logoWrapper}>
            <Typography.Text className={clsx(styles.logoText, styles[variant])}>
                {settings ? settings.portal_name : t('Data Product Portal')}
            </Typography.Text>
        </Flex>
    );
}
