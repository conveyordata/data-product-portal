import { Flex, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import {
    AccessDurationType,
    useGetOutputPortAccessDurationsQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { DataProductChoiceOptions } from '@/store/features/cart/cart-slice.ts';

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

    const { label } = useMemo(() => {
        if (!accessDurations) {
            return { label: '', isPermanent: true };
        }
        const abstractTypeAccessDuration =
            dataProductTypeChoice === DataProductChoiceOptions.data_product
                ? accessDurations?.data_product_access_duration
                : accessDurations?.exploration_access_duration;
        const isPermanent = abstractTypeAccessDuration.access_duration_type === AccessDurationType.Permanent;
        return {
            label: isPermanent
                ? t('Permanent access')
                : t('Timebound access ({{count}} days)', {
                      count: abstractTypeAccessDuration.days,
                  }),
            isPermanent,
        };
    }, [accessDurations, dataProductTypeChoice, t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <Flex align="center" gap="small">
            <Typography.Text type="secondary">{label}</Typography.Text>
        </Flex>
    );
}
