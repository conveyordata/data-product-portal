import { Divider, Flex, Space, Typography } from 'antd';

import { DataProductSettingContract, DataProductSettingValueContract } from '@/types/data-product-setting';

import { SettingsCard } from './components/settings-card.component';
import styles from './data-product-settings.module.scss';

type Props = {
    settings?: DataProductSettingContract[];
    settingValues?: DataProductSettingValueContract[];
    updateSetting: (setting_id: string, value: string) => void;
};

export function CustomSettings({ settings = [], settingValues = [], updateSetting }: Props) {
    const settingsWithValues = settings.map((setting) => {
        const settingsValue = settingValues.find((settingValue) => settingValue.data_product_setting_id === setting.id);
        return {
            setting: setting,
            value: settingsValue?.value ?? setting.default,
            isDefault: !settingsValue,
        };
    });

    const groupedSettings = Object.entries(
        settingsWithValues.reduce<Record<string, typeof settingsWithValues>>((acc, item) => {
            const category = item.setting.category;
            if (!acc[category]) {
                acc[category] = [];
            }
            acc[category].push(item);
            return acc;
        }, {}),
    );

    return (
        <Flex vertical>
            {groupedSettings.map(([category, categorySettings = []], index) => (
                <Flex vertical className={styles.container}>
                    <Typography.Title level={3}>{category}</Typography.Title>
                    <Space direction="vertical">
                        {categorySettings.map((setting) => (
                            <SettingsCard {...setting} updateSetting={updateSetting} />
                        ))}
                    </Space>
                    {groupedSettings.length - 1 != index && <Divider />}
                </Flex>
            ))}
        </Flex>
    );
}
