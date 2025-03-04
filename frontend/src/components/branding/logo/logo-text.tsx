import { Typography } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import styles from './logo-text.module.scss';

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
