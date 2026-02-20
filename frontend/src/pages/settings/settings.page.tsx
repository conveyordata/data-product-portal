import { SettingOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { SettingsTabs } from './components/settings-tabs/settings-tabs.component.tsx';
import styles from './settings.module.scss';

export function Settings() {
    const { t } = useTranslation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        {' '}
                        <SettingOutlined /> {t('Settings')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);
    return (
        <div className={styles.container}>
            <SettingsTabs />
        </div>
    );
}
