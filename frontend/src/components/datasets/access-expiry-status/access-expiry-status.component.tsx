import { ClockCircleOutlined } from '@ant-design/icons';
import { Flex, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { DecisionStatus } from '@/types/roles';
import { formatDateFromISOString } from '@/utils/date.helper.ts';

type Props = {
    expiresOn?: string | null;
    isExpiringSoon: boolean;
    status: DecisionStatus;
};

export default function AccessExpiryStatus({ expiresOn, isExpiringSoon, status }: Props) {
    const { t } = useTranslation();
    return (
        <Flex gap="small" align="center">
            <Typography.Text>{expiresOn ? formatDateFromISOString(expiresOn) : t('Never')}</Typography.Text>
            {isExpiringSoon && status !== DecisionStatus.Expired && (
                <Tag color="warning" icon={<ClockCircleOutlined />} style={{ width: 'fit-content' }}>
                    {t('Expiring soon')}
                </Tag>
            )}
        </Flex>
    );
}
