import styles from './sidebar-logo.module.scss';
import { Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

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
