import { ToolOutlined } from '@ant-design/icons';
import { Result } from 'antd';
import { useTranslation } from 'react-i18next';

export default function UnderConstruction() {
    const { t } = useTranslation();
    return (
        <div style={{ padding: '48px 0' }}>
            <Result
                icon={<ToolOutlined style={{ color: '#1677ff' }} />}
                title={t('Under Construction')}
                subTitle={t('We are currently working hard to build this feature. Please check back soon!')}
            />
        </div>
    );
}
