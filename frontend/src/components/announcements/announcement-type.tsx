import { ExclamationCircleOutlined, InfoCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { Flex, type GlobalToken, Tooltip, theme } from 'antd';
import type { TFunction } from 'i18next';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { AnnouncementType } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

export const ANNOUNCEMENT_URGENCY = [AnnouncementType.ActionNeeded, AnnouncementType.Warning, AnnouncementType.Info];

type AnnouncementTypeConfig = {
    label: string;
    meaning: string;
    color: string;
    icon: ReactNode;
};

export function getAnnouncementTypeConfig(
    t: TFunction,
    token: GlobalToken,
): Record<AnnouncementType, AnnouncementTypeConfig> {
    return {
        [AnnouncementType.ActionNeeded]: {
            label: t('Action needed'),
            meaning: t('Consumers must change something: a deprecation, retirement or breaking change.'),
            color: token.colorError,
            icon: <ExclamationCircleOutlined />,
        },
        [AnnouncementType.Warning]: {
            label: t('Warning'),
            meaning: t('Something is wrong or will be: late or incomplete data, an incident or planned maintenance.'),
            color: token.colorWarning,
            icon: <WarningOutlined />,
        },
        [AnnouncementType.Info]: {
            label: t('Info'),
            meaning: t('News that needs no action, such as a new version.'),
            color: token.colorTextTertiary,
            icon: <InfoCircleOutlined />,
        },
    };
}

export function AnnouncementTypeIcon({ type }: { type: AnnouncementType }) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const { label, color, icon } = getAnnouncementTypeConfig(t, token)[type];
    return (
        <Tooltip title={label}>
            <span role="img" aria-label={label} style={{ color }}>
                {icon}
            </span>
        </Tooltip>
    );
}

export function AnnouncementTypeLabel({ type }: { type: AnnouncementType }) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const { label, color, icon } = getAnnouncementTypeConfig(t, token)[type];
    return (
        <Flex gap="small" align="center">
            <span style={{ color }}>{icon}</span>
            {label}
        </Flex>
    );
}
