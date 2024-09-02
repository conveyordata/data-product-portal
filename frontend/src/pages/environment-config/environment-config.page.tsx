import styles from './environment-config.module.scss';
import { Typography, Flex, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { DynamicPathParams } from '@/types/navigation';
import { useGetEnvConfigByIdQuery } from '@/store/features/environments/environments-api-slice';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { Input } from 'antd/lib';

const { TextArea } = Input;

export function EnvironmentConfig() {
    const { t } = useTranslation();
    const { envConfigId = '' } = useParams<DynamicPathParams>();
    const { data: envConfig, isLoading } = useGetEnvConfigByIdQuery(envConfigId, { skip: !envConfigId });

    if (isLoading) return <LoadingSpinner />;

    if (!envConfig) return null;

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3}>{t('Environment Configuration')}</Typography.Title>
            <div className={styles.textareaContainer}>
                <TextArea autoSize={{ minRows: 5 }} value={JSON.stringify(envConfig.config, null, 4)} disabled />
            </div>
        </Flex>
    );
}
