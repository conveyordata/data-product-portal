import Icon from '@ant-design/icons';
import type { ComponentProps } from 'react';
import ProductLogoIcon from '@/assets/icons/logo.svg?react';
import DataProductOutlinedIcon from '@/assets/icons/outline-icons/data-product-outline-icon.svg?react';
import ExplorationOutlinedIcon from '@/assets/icons/outline-icons/exploration-outline-icon.svg?react';
import OutputPortOutlinedIcon from '@/assets/icons/outline-icons/output-port-outline-icon.svg?react';
import TechnicalAssetOutlineIcon from '@/assets/icons/outline-icons/technical-asset-outline-icon.svg?react';
import type { AbstractDataProductType } from '@/store/api/services/generated/usersApi.ts';
import styles from './index.module.scss';

type IconProps = Omit<ComponentProps<typeof Icon>, 'component'>;

export function ProductLogo(props: IconProps) {
    return <Icon component={ProductLogoIcon} {...props} />;
}

export function DataProductOutlined(props: IconProps) {
    return <Icon component={DataProductOutlinedIcon} {...props} />;
}

export function ExplorationOutlined(props: IconProps) {
    return <Icon component={ExplorationOutlinedIcon} {...props} />;
}

export function OutputPortOutlined(props: IconProps) {
    return <Icon component={OutputPortOutlinedIcon} {...props} />;
}

export function TechnicalAssetOutlined(props: IconProps) {
    return <Icon component={TechnicalAssetOutlineIcon} {...props} />;
}

export function ConsumersIcon() {
    return (
        <span className={styles.combinedIcon}>
            <DataProductOutlined />
            <ExplorationOutlined />
        </span>
    );
}

export function AbstractProductIcon({ type }: { type: AbstractDataProductType }) {
    switch (type) {
        case 'data_products':
            return <DataProductOutlined />;
        case 'explorations':
            return <ExplorationOutlined />;
        default:
            return null;
    }
}
