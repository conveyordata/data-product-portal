import { ClockCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { Flex, Typography } from 'antd';
import { differenceInCalendarDays, parseISO } from 'date-fns';
import { useTranslation } from 'react-i18next';
import { useGetExpiringSoonThresholdQuery } from '@/store/api/services/generated/accessDurationsApi.ts';
import { InputPortStatus, RenewalStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { formatDateFromISOString } from '@/utils/date.helper.ts';

export const DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS = 14;

export function isExpiringSoon(status: string, validUntil: string | null, thresholdDays: number): boolean {
    if (status !== InputPortStatus.Approved || validUntil === null) {
        return false;
    }
    const daysUntilExpiry = differenceInCalendarDays(parseISO(validUntil), new Date());
    return daysUntilExpiry >= 0 && daysUntilExpiry <= thresholdDays;
}

type RenewalTagProps = {
    status: string;
    renewalStatus?: string | null;
};

export function RenewalTag({ status, renewalStatus }: RenewalTagProps) {
    const { t } = useTranslation();
    if (status === InputPortStatus.Pending) {
        return null;
    }
    if (renewalStatus === RenewalStatus.Pending) {
        return (
            <Flex align={'center'} gap={'small'}>
                <ClockCircleOutlined />
                <Typography.Text type={'secondary'}>{t('Renewal pending')}</Typography.Text>
            </Flex>
        );
    }
    if (renewalStatus === RenewalStatus.Denied) {
        return (
            <Flex align={'center'} gap={'small'}>
                <CloseCircleOutlined />
                <Typography.Text type={'secondary'}>{t('Renewal declined')}</Typography.Text>
            </Flex>
        );
    }
    return null;
}

type IsExpiringSoonTagProps = {
    status: string;
    validUntil: string | null;
    renewalStatus?: string | null;
};

export function IsExpiringSoonTag({ status, validUntil, renewalStatus }: IsExpiringSoonTagProps) {
    const { t } = useTranslation();
    const { data } = useGetExpiringSoonThresholdQuery();
    const thresholdDays = data?.days ?? DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS;
    if (renewalStatus === RenewalStatus.Pending || !isExpiringSoon(status, validUntil, thresholdDays)) {
        return null;
    }
    return (
        <Flex align={'center'} gap={'small'}>
            <ExclamationCircleOutlined />
            <Typography.Text type={'secondary'}>{t('Expiring soon')}</Typography.Text>
        </Flex>
    );
}

type ExpiryDateProps = {
    status: string;
    validUntil: string | null;
};

export function ExpiryDate({ status, validUntil }: ExpiryDateProps) {
    const { t } = useTranslation();
    if (status === InputPortStatus.Pending || status === InputPortStatus.Denied) {
        return null;
    }
    if (validUntil === null) {
        return <Typography.Text type={'secondary'}>{t('Permanent access')}</Typography.Text>;
    }
    return <Typography.Text>{formatDateFromISOString(validUntil)}</Typography.Text>;
}
