import { ToolOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/empty-state/empty-state.component.tsx';

export function PlatformTab() {
    const { t } = useTranslation();
    return (
        <EmptyState
            icon={<ToolOutlined />}
            title={t('Under construction')}
            description={t('Platform configuration is not available yet.')}
        />
    );
}
