import { Empty, Typography } from 'antd';
import styles from './roles-tab.module.scss';
import { useTranslation } from 'react-i18next';

export function RolesTab() {
    const { t } = useTranslation();
    return (
        <div>
            <Empty description={<Typography.Text>{t('Under construction')}</Typography.Text>} />
        </div>
    );
}
