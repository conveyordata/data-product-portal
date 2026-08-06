import { Tag, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';

type AccessModeDisplay = {
    id: string;
    name: string;
    description: string;
};
type Props = {
    accessMode?: AccessModeDisplay | null;
};

export default function AccessMode({ accessMode }: Props) {
    const { t } = useTranslation();
    if (!accessMode) {
        return t('None');
    }
    return (
        <Tooltip key={accessMode.id} title={accessMode.description || undefined}>
            <Tag>{accessMode.name}</Tag>
        </Tooltip>
    );
}
