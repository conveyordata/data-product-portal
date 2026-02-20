import { UnorderedListOutlined } from '@ant-design/icons';
import { Empty, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';

export function AuditLogs() {
    const { t } = useTranslation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        {' '}
                        <UnorderedListOutlined /> {t('Audit Logs')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);
    return (
        <div>
            {/* <Typography.Title level={3}>{t('Audit Logs')}</Typography.Title> */}
            <Empty description={<Typography.Text>{t('Under construction')}</Typography.Text>} />
        </div>
    );
}
