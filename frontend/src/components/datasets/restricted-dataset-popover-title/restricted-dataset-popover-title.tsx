import { useTranslation } from 'react-i18next';
import { Space, Typography, TypographyProps } from 'antd';

type Props = {
    name: string;
    titleProps?: TypographyProps['Text'];
    isApproved?: boolean;
};

export function RestrictedDatasetPopoverTitle({ name, titleProps, isApproved }: Props) {
    const { t } = useTranslation();
    const subtitle = isApproved ? t('Access granted') : t('Permission required');

    return (
        <Space>
            <Typography.Text {...titleProps}>{name}</Typography.Text>
            <Typography.Text italic>({subtitle})</Typography.Text>
        </Space>
    );
}
