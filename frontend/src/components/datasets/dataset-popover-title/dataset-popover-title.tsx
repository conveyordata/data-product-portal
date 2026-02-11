import { Space, Typography, type TypographyProps } from 'antd';
import { useTranslation } from 'react-i18next';

import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';

type Props = {
    name: string;
    accessType: OutputPortAccessType;
    titleProps?: TypographyProps['Text'];
    isApproved?: boolean;
};

export function DatasetPopoverTitle({ name, accessType, titleProps, isApproved }: Props) {
    const { t } = useTranslation();
    const subtitle = isApproved ? t('Access granted') : t('Permission required');

    return (
        <Space>
            <Typography.Text {...titleProps}>{name}</Typography.Text>
            {accessType !== OutputPortAccessType.Public && <Typography.Text italic>({subtitle})</Typography.Text>}
        </Space>
    );
}
