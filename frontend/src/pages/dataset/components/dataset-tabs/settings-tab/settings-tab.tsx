import styles from './settings-tab.module.scss';
import { Flex } from 'antd';
import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';

type Props = {
    datasetId: string | undefined;
};

export function SettingsTab({ datasetId }: Props) {
    return (
        <Flex vertical className={styles.container}>
            <DataProductSettings dataProductId={datasetId} scope={'dataset'} />
        </Flex>
    );
}
