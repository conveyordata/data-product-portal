import Icon, { ApiOutlined, AppstoreOutlined, DatabaseOutlined, ExperimentOutlined } from '@ant-design/icons';
import type { ComponentProps } from 'react';
import ProductLogoIcon from '@/assets/icons/logo.svg?react';
import type { AbstractDataProductType } from '@/store/api/services/generated/usersApi.ts';
import styles from './index.module.scss';

type IconProps = Omit<ComponentProps<typeof Icon>, 'component'>;

export function ProductLogo(props: IconProps) {
    return <Icon component={ProductLogoIcon} {...props} />;
}

export function DataProductOutlined(props: IconProps) {
    return <AppstoreOutlined {...props} />;
}

export function ExplorationOutlined(props: IconProps) {
    return <ExperimentOutlined {...props} />;
}

export function OutputPortOutlined(props: IconProps) {
    return <ApiOutlined {...props} />;
}

export function TechnicalAssetOutlined(props: IconProps) {
    return <DatabaseOutlined {...props} />;
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
