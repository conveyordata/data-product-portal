import { Empty, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

export function AuditLogs() {
    const { t } = useTranslation();
    return (
        <div>
            {/* <Typography.Title level={3}>{t('Audit Logs')}</Typography.Title> */}
            <Empty description={
                <Typography.Text>
                    {t("Under construction")}
                </Typography.Text>
            }/>
        </div>
    );
}
