import styles from './logo-text.module.scss';
import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

type Props = {
    variant?: 'light' | 'dark';
};

export function LogoText({ variant = 'light' }: Props) {
    const { t } = useTranslation();
    return (
        <Typography.Title level={4} className={clsx(styles.logoText, styles[variant])}>
            {t('Logo')}
        </Typography.Title>
    );
}
