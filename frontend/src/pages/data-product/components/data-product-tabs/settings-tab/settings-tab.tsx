import { Flex } from 'antd';

import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';

import styles from './settings-tab.module.scss';

type Props = {
    dataProductId: string | undefined;
};

export function SettingsTab({ dataProductId }: Props) {
    return (
        <Flex vertical className={styles.container}>
            <DataProductSettings id={dataProductId} scope={'dataproduct'} />
        </Flex>
    );
}
