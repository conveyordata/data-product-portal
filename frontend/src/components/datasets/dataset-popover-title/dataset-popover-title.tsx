import { Space, Typography, TypographyProps } from 'antd';
import { useTranslation } from 'react-i18next';

import { DatasetAccess } from '@/types/dataset';

type Props = {
    name: string;
    accessType: DatasetAccess;
    titleProps?: TypographyProps['Text'];
    isApproved?: boolean;
};

export function DatasetPopoverTitle({ name, accessType, titleProps, isApproved }: Props) {
    const { t } = useTranslation();
    const subtitle = isApproved ? t('Access granted') : t('Permission required');

    return (
        <Space>
            <Typography.Text {...titleProps}>{name}</Typography.Text>
            {accessType !== DatasetAccess.Public && <Typography.Text italic>({subtitle})</Typography.Text>}
        </Space>
    );
}
