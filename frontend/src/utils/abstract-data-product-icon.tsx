import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import type { ComponentType, ForwardRefExoticComponent, SVGProps } from 'react';
import explorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import { AbstractDataProductType } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';

export const getAbstractDataProductIcon = (
    type: AbstractDataProductType,
):
    | ComponentType<CustomIconComponentProps | SVGProps<SVGSVGElement>>
    | ForwardRefExoticComponent<CustomIconComponentProps>
    | undefined => {
    switch (type) {
        case AbstractDataProductType.DataProducts:
            return getDataProductTypeIcon();
        case AbstractDataProductType.Explorations:
            return explorationBorderIcon;
        default:
            return undefined;
    }
};
