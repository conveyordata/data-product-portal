import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

export function Settings() {
    const { t } = useTranslation();

    return <Typography.Title level={3}>{t('Settings')}</Typography.Title>;
}
