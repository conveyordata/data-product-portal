import Icon from '@ant-design/icons';
import type { ComponentProps } from 'react';

import DataProductOutlinedIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import DatasetOutlinedIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import ProductLogoIcon from '@/assets/icons/logo.svg?react';

type IconProps = Omit<ComponentProps<typeof Icon>, 'component'>;

export function ProductLogo(props: IconProps) {
    return <Icon component={ProductLogoIcon} {...props} />;
}

export function DataProductOutlined(props: IconProps) {
    return <Icon component={DataProductOutlinedIcon} {...props} />;
}

export function DatasetOutlined(props: IconProps) {
    return <Icon component={DatasetOutlinedIcon} {...props} />;
}
