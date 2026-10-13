import { Flex, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataProductEnvironment } from '@/store/api/services/generated/dataProductsApi.ts';

type Props = {
    environments: DataProductEnvironment[];
};

export function EnvironmentsField({ environments }: Props) {
    const { t } = useTranslation();

    return (
        <Flex wrap align="center" gap="small">
            <Typography.Text strong>{t('Environments')}</Typography.Text>
            {environments.map(({ environment }) => (
                <Tag key={environment.id}>{environment.name}</Tag>
            ))}
        </Flex>
    );
}
