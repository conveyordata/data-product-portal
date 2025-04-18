import { FullExplorer } from '@/components/explorer/explorer';
import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

export function ExplorerPage() {
    const { t } = useTranslation();
    return (
        <div>
            <Typography.Title level={3}>{t('Explorer')}</Typography.Title>
            <div style={{ height: '80vh' }}>
                <FullExplorer></FullExplorer>
            </div>
        </div>
    );
}
