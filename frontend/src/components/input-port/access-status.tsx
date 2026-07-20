import { Tag, Typography } from 'antd';
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
    renewalStatus?: string | null;
};

export function RenewalTag({ renewalStatus }: RenewalTagProps) {
    const { t } = useTranslation();
    if (renewalStatus === RenewalStatus.Pending) {
        return <Tag color={'blue'}>{t('Renewal pending')}</Tag>;
    }
    if (renewalStatus === RenewalStatus.Denied) {
        return <Tag color={'red'}>{t('Renewal declined')}</Tag>;
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
    return <Tag color={'gold'}>{t('Expiring soon')}</Tag>;
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
