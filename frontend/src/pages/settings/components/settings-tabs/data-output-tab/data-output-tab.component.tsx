import { Empty, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

export function DataOutputTab() {
    const { t } = useTranslation();
    return (
        <div>
            <Empty description={<Typography.Text>{t('Under construction')}</Typography.Text>} />
        </div>
    );
}
