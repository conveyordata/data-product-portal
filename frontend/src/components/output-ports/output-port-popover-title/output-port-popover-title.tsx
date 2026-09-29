import { Space, Typography, type TypographyProps } from 'antd';
import { useTranslation } from 'react-i18next';

import {
    OutputPortAccessFunction,
    type OutputPortClassification,
} from '@/store/api/services/generated/dataProductsApi.ts';

const { Text } = Typography;

type Props = {
    name: string;
    classification: OutputPortClassification;
    titleProps?: TypographyProps;
    isApproved?: boolean;
};

export function OutputPortPopoverTitle({ name, classification, titleProps, isApproved }: Props) {
    const { t } = useTranslation();
    const subtitle = isApproved ? t('Access granted') : t('Permission required');

    return (
        <Space>
            <Text {...titleProps}>{name}</Text>
            {classification.access_function !== OutputPortAccessFunction.Unrestricted && (
                <Text italic>
                    ({classification.name} · {subtitle})
                </Text>
            )}
        </Space>
    );
}
