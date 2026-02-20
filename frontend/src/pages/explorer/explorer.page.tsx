import { CompassOutlined } from '@ant-design/icons';
import { Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FullExplorer } from '@/components/global-explorer/full-explorer.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import styles from './explorer.page.module.scss';

export function ExplorerPage() {
    const { t } = useTranslation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        {' '}
                        <CompassOutlined /> {t('Explorer')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);
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
