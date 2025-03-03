import { Flex, Typography } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import styles from './sidebar-logo.module.scss';

type Props = {
    variant?: 'light' | 'dark';
};

export function SidebarLogo({ variant = 'light' }: Props) {
    const { t } = useTranslation();
    return (
        <Flex vertical className={styles.logoWrapper}>
            <Typography.Text className={clsx(styles.logoText, styles[variant])}>{t('Logo')}</Typography.Text>
        </Flex>
    );
}
