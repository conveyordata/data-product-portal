import { DisconnectOutlined } from '@ant-design/icons';
import { Tag, Tooltip, theme } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    iconOnly?: boolean;
};

export function NotShareableIcon({ iconOnly }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();

    return (
        <Tooltip title={t('Technical Assets of this type cannot be linked to an Output Port')}>
            {iconOnly ? (
                <DisconnectOutlined style={{ color: token.colorTextSecondary }} />
            ) : (
                <Tag icon={<DisconnectOutlined />}>{t('Not shareable')}</Tag>
            )}
        </Tooltip>
    );
}
