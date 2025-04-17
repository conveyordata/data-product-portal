import { Explorer } from '@/components/explorer/explorer';
import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

export function ExplorerPage() {
    const { t } = useTranslation();
    return (
        <div>
            <Typography.Title level={3}>{t('Explorer')}</Typography.Title>
            <div style={{ height: '80vh' }}>
                <Explorer id={'ffcf5286-8f14-4411-8dfe-75dc7ed9ec36'} type={'dataproduct'} ></Explorer>
            </div>
        </div>
    );
}
