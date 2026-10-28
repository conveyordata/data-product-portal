import { Flex, Space, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import AccessMode from '@/components/access-modes/access-mode.component.tsx';

type AccessModeDisplay = {
    id: string;
    name: string;
    description: string;
};

type Props = {
    accessModes: AccessModeDisplay[];
    className?: string;
};

export function AccessModesField({ accessModes, className }: Props) {
    const { t } = useTranslation();

    return (
        <Flex className={className} align="center" gap={8}>
            <Typography.Text strong>{t('Access modes')}</Typography.Text>
            {accessModes.length === 0 ? (
                <Typography.Text>{t('None')}</Typography.Text>
            ) : (
                <Space size={[4, 4]} wrap>
                    {accessModes.map((accessMode) => (
                        <AccessMode key={accessMode.id} accessMode={accessMode} />
                    ))}
                </Space>
            )}
        </Flex>
    );
}
