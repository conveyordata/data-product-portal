import { Tag, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';

export function NotShareableTag() {
    const { t } = useTranslation();

    return (
        <Tooltip title={t('Technical Assets of this type cannot be linked to an Output Port')}>
            <Tag>{t('Not shareable')}</Tag>
        </Tooltip>
    );
}
