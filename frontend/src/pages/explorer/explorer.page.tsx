import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { FullExplorer } from '@/components/explorer/explorer';
import styles from './explorer.page.module.scss';

export function ExplorerPage() {
    const { t } = useTranslation();
    return (
        <div className={styles.explorerPage}>
            <Typography.Title level={3} className={styles.title}>
                {t('Explorer')}
            </Typography.Title>
            <div className={styles.explorerContainer}>
                <FullExplorer />
            </div>
        </div>
    );
}
