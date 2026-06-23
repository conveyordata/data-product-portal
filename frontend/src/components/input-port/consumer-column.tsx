import { Badge } from 'antd';
import { useTranslation } from 'react-i18next';
import explorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    type AbstractDataProductInfo,
    AbstractDataProductType,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { createAbstractDataProductIdPath } from '@/types/navigation.ts';
import type { DecisionStatus } from '@/types/roles';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';

type Props = {
    status: DecisionStatus;
    consumingAbstractDataProductId: string;
    consumingAbstractDataProduct: AbstractDataProductInfo;
};
export function ConsumerColumn({ consumingAbstractDataProduct, status, consumingAbstractDataProductId }: Props) {
    const { t } = useTranslation();
    const popover = (() => {
        switch (consumingAbstractDataProduct.abstract_data_product_type) {
            case AbstractDataProductType.DataProducts:
                return t('The consumer is a Data Product named: {{name}}', { name: consumingAbstractDataProduct.name });
            case AbstractDataProductType.Explorations:
                return t('The consumer is an Exploration named: {{name}}', { name: consumingAbstractDataProduct.name });
            default:
                return undefined;
        }
    })();
    const { data: dataProduct } = useGetDataProductQuery(consumingAbstractDataProductId, {
        skip: consumingAbstractDataProduct.abstract_data_product_type !== AbstractDataProductType.DataProducts,
    });
    const icon = (() => {
        switch (consumingAbstractDataProduct.abstract_data_product_type) {
            case AbstractDataProductType.DataProducts:
                return getDataProductTypeIcon(dataProduct?.type?.icon_key);
            case AbstractDataProductType.Explorations:
                return explorationBorderIcon;
            default:
                return undefined;
        }
    })();
    return (
        <TableCellAvatar
            popover={{ title: popover }}
            linkTo={createAbstractDataProductIdPath(
                consumingAbstractDataProductId,
                consumingAbstractDataProduct.abstract_data_product_type,
            )}
            icon={<CustomSvgIconLoader iconComponent={icon} hasRoundBorder size={'default'} />}
            title={consumingAbstractDataProduct.name}
            subtitle={<Badge status={getDecisionStatusBadgeStatus(status)} text={getDecisionStatusLabel(t, status)} />}
        />
    );
}
