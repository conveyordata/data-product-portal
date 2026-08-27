import { useTranslation } from 'react-i18next';
import explorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import BlurredText from '@/components/blurred/blurred-text.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    type AbstractDataProductInfo,
    AbstractDataProductType,
    type User,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { createAbstractDataProductIdPath } from '@/types/navigation.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';

type Props = {
    requestedBy: User;
    consumingAbstractDataProductId: string;
    consumingAbstractDataProduct: AbstractDataProductInfo;
};
export function ConsumerColumn({ consumingAbstractDataProduct, consumingAbstractDataProductId, requestedBy }: Props) {
    const { t } = useTranslation();
    const popover = (() => {
        switch (consumingAbstractDataProduct.abstract_data_product_type) {
            case AbstractDataProductType.DataProducts:
                if (consumingAbstractDataProduct.is_redacted) {
                    return t(
                        'The consumer is a hidden Data Product, contact the requester ({{ requester }}) for more information',
                        { requester: requestedBy.email },
                    );
                }
                return t('The consumer is a Data Product named: {{name}}', { name: consumingAbstractDataProduct.name });
            case AbstractDataProductType.Explorations:
                return t('The consumer is an Exploration named: {{name}}', { name: consumingAbstractDataProduct.name });
            default:
                return undefined;
        }
    })();
    const { data: dataProduct } = useGetDataProductQuery(consumingAbstractDataProductId, {
        skip:
            consumingAbstractDataProduct.abstract_data_product_type !== AbstractDataProductType.DataProducts ||
            consumingAbstractDataProduct.is_redacted,
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
            linkTo={
                consumingAbstractDataProduct.is_redacted
                    ? undefined
                    : createAbstractDataProductIdPath(
                          consumingAbstractDataProductId,
                          consumingAbstractDataProduct.abstract_data_product_type,
                      )
            }
            icon={<CustomSvgIconLoader iconComponent={icon} hasRoundBorder size="default" />}
            title={
                consumingAbstractDataProduct.is_redacted ? (
                    <BlurredText>{consumingAbstractDataProduct.name}</BlurredText>
                ) : (
                    consumingAbstractDataProduct.name
                )
            }
        />
    );
}
