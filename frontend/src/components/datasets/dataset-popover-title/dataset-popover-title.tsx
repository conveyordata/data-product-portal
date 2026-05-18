import { Space, Typography, type TypographyProps } from 'antd';
import { useTranslation } from 'react-i18next';

import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';

const { Text } = Typography;

type Props = {
    name: string;
    accessType: OutputPortAccessType;
    titleProps?: TypographyProps;
    isApproved?: boolean;
};

export function DatasetPopoverTitle({ name, accessType, titleProps, isApproved }: Props) {
    const { t } = useTranslation();
    const subtitle = isApproved ? t('Access granted') : t('Permission required');

    return (
        <Space>
            <Text {...titleProps}>{name}</Text>
            {accessType !== OutputPortAccessType.Unrestricted && <Text italic>({subtitle})</Text>}
        </Space>
    );
}
