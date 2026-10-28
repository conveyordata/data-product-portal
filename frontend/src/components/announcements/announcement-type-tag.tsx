import {
    CloseCircleOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined,
    RocketOutlined,
    ToolOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';
import type { TFunction } from 'i18next';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { AnnouncementType } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

type AnnouncementTypeConfig = {
    label: string;
    meaning: string;
    color: string;
    icon: ReactNode;
};

export function getAnnouncementTypeConfig(t: TFunction): Record<AnnouncementType, AnnouncementTypeConfig> {
    return {
        [AnnouncementType.Issue]: {
            label: t('Issue'),
            meaning: t('The data is wrong, late or missing right now.'),
            color: 'red',
            icon: <CloseCircleOutlined />,
        },
        [AnnouncementType.ActionNeeded]: {
            label: t('Action needed'),
            meaning: t('Consumers must change something: a deprecation, retirement or breaking change.'),
            color: 'red',
            icon: <ExclamationCircleOutlined />,
        },
        [AnnouncementType.PlannedMaintenance]: {
            label: t('Planned maintenance'),
            meaning: t('Temporary downtime or delay in a known window.'),
            color: 'gold',
            icon: <ToolOutlined />,
        },
        [AnnouncementType.NewVersion]: {
            label: t('New version'),
            meaning: t('Something improved. Nothing breaks on the consumer side.'),
            color: 'blue',
            icon: <RocketOutlined />,
        },
        [AnnouncementType.Info]: {
            label: t('Info'),
            meaning: t('General news.'),
            color: 'default',
            icon: <InfoCircleOutlined />,
        },
    };
}

export function AnnouncementTypeTag({ type }: { type: AnnouncementType }) {
    const { t } = useTranslation();
    const { label, color, icon } = getAnnouncementTypeConfig(t)[type];
    return (
        <Tag color={color} icon={icon}>
            {label}
        </Tag>
    );
}
