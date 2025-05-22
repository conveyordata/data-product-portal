import { Flex } from 'antd';
import { useCallback } from 'react';

import { CustomSettings } from '@/components/custom-settings/custom-settings.component';
import { useCreateDataProductSettingValueMutation } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { DataProductSettingValueCreateRequest } from '@/types/data-product-setting';

import styles from './settings-tab.module.scss';

type Props = {
    dataProductId: string;
};

export function SettingsTab({ dataProductId }: Props) {
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [updateDataProductSetting] = useCreateDataProductSettingValueMutation();

    const updateSetting = useCallback(
        async (setting_id: string, value: string) => {
            try {
                const request: DataProductSettingValueCreateRequest = {
                    data_product_id: dataProductId,
                    data_product_settings_id: setting_id,
                    value: value,
                };
                await updateDataProductSetting(request).unwrap();
            } catch (_) {
                const errorMessage = 'Failed to update setting';
                dispatchMessage({ content: errorMessage, type: 'error' });
            }
        },
        [updateDataProductSetting, dataProductId],
    );

    return (
        <Flex vertical className={styles.container}>
            <CustomSettings settings={dataProduct?.settings} updateSetting={updateSetting} />
        </Flex>
    );
}
