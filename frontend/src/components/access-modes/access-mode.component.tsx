import { Tag, Tooltip } from 'antd';
import type { ComponentProps } from 'react';
import { useTranslation } from 'react-i18next';

type AccessModeDisplay = {
    id: string;
    name: string;
    description: string;
};
type Props = {
    accessMode?: AccessModeDisplay | null;
    tagProps?: ComponentProps<typeof Tag>;
};

export default function AccessMode({ accessMode, tagProps }: Props) {
    const { t } = useTranslation();
    if (!accessMode) {
        return t('None');
    }
    return (
        <Tooltip key={accessMode.id} title={accessMode.description || undefined}>
            <Tag {...tagProps}>{accessMode.name}</Tag>
        </Tooltip>
    );
}
