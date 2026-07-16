import { Tag, Typography } from 'antd';
import { differenceInCalendarDays, parseISO } from 'date-fns';
import { useTranslation } from 'react-i18next';
import { InputPortStatus, RenewalStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { formatDateFromISOString } from '@/utils/date.helper.ts';

export const EXPIRING_SOON_THRESHOLD_DAYS = 14;

function isExpiringSoon(status: string, validUntil: string | null): boolean {
    if (status !== InputPortStatus.Approved || validUntil === null) {
        return false;
    }
    const daysUntilExpiry = differenceInCalendarDays(parseISO(validUntil), new Date());
    return daysUntilExpiry >= 0 && daysUntilExpiry <= EXPIRING_SOON_THRESHOLD_DAYS;
}

type RenewalTagProps = {
    status: string;
    renewalStatus?: string | null;
    validUntil: string | null;
};

export function RenewalTag({ status, renewalStatus, validUntil }: RenewalTagProps) {
    const { t } = useTranslation();
    if (status === InputPortStatus.Pending) {
        return null;
    }
    if (renewalStatus === RenewalStatus.Pending) {
        return <Tag color={'blue'}>{t('Renewal pending')}</Tag>;
    }
    if (renewalStatus === RenewalStatus.Denied && status !== InputPortStatus.Denied) {
        return <Tag color={'red'}>{t('Renewal declined')}</Tag>;
    }
    if (isExpiringSoon(status, validUntil)) {
        return <Tag color={'gold'}>{t('Expiring soon')}</Tag>;
    }
    return null;
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
        return <Typography.Text type={'secondary'}>{t('Permanent Access')}</Typography.Text>;
    }
    return <Typography.Text>{formatDateFromISOString(validUntil)}</Typography.Text>;
}
