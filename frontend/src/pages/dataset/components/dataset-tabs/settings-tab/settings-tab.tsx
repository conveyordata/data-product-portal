import { Flex } from 'antd';

import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';

import styles from './settings-tab.module.scss';

type Props = {
    datasetId: string;
    dataProductId: string;
};

export function SettingsTab({ datasetId, dataProductId }: Props) {
    return (
        <Flex vertical className={styles.container}>
            <DataProductSettings id={datasetId} scope={'dataset'} dataProductId={dataProductId} />
        </Flex>
    );
}
