import { Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import {
    AccessDurationType,
    useGetOutputPortAccessDurationsQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { DataProductChoiceOptions } from '@/store/features/cart/cart-slice.ts';
import { formatDate } from '@/utils/date.helper.ts';

type Props = {
    outputPort: SearchOutputPortsResponseItem;
    dataProductTypeChoice: DataProductChoiceOptions;
};

export function OutputPortAccessDuration({ outputPort, dataProductTypeChoice }: Props) {
    const { data: accessDurations, isLoading } = useGetOutputPortAccessDurationsQuery({
        id: outputPort.id,
        dataProductId: outputPort.data_product_id,
    });
    const { t } = useTranslation();

    const accessDurationString = useMemo(() => {
        if (!accessDurations) {
            return '';
        }
        const abstractTypeAccessDuration =
            dataProductTypeChoice === DataProductChoiceOptions.data_product
                ? accessDurations?.data_product_access_duration
                : accessDurations?.exploration_access_duration;
        const expiryDate = new Date(Date.now() + abstractTypeAccessDuration.days * 24 * 60 * 60 * 1000);
        return abstractTypeAccessDuration.access_duration_type === AccessDurationType.Permanent
            ? t('permanent')
            : t('{{count}} days, access will expire on {{expiryDate}}', {
                  count: abstractTypeAccessDuration.days,
                  expiryDate: formatDate(expiryDate),
              });
    }, [accessDurations, dataProductTypeChoice, t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <Typography.Text>
            <Typography.Text>{outputPort.name}:</Typography.Text> {accessDurationString}
        </Typography.Text>
    );
}
