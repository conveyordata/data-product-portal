import { Flex } from 'antd';
import { useCallback } from 'react';

import { CustomSettings } from '@/components/data-products/data-product-settings/custom-settings.component';
import { useCreateDatasetSettingValueMutation } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataProductSettingValueCreateRequest } from '@/types/data-product-setting';

import styles from './settings-tab.module.scss';

type Props = {
    datasetId: string;
};

export function SettingsTab({ datasetId }: Props) {
    const { data: dataset } = useGetDatasetByIdQuery(datasetId);
    const [updateDatasetSetting] = useCreateDatasetSettingValueMutation();

    const updateSetting = useCallback(
        async (setting_id: string, value: string) => {
            try {
                const request: DataProductSettingValueCreateRequest = {
                    data_product_id: datasetId,
                    data_product_settings_id: setting_id,
                    value: value,
                };
                await updateDatasetSetting(request).unwrap();
            } catch (_) {
                const errorMessage = 'Failed to update setting';
                dispatchMessage({ content: errorMessage, type: 'error' });
            }
        },
        [updateDatasetSetting, datasetId],
    );

    return (
        <Flex vertical className={styles.container}>
            <CustomSettings settings={dataset?.settings} updateSetting={updateSetting} />
        </Flex>
    );
}
