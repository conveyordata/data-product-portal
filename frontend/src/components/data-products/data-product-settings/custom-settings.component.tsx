import { Card, Divider, Flex, Space, Typography } from 'antd';

import { CustomSettingValueContract } from '@/types/data-product-setting';

import { SettingsCardHeader } from './components/settings-card-header.component';
import { SettingsForm } from './components/settings-form.component';
import styles from './data-product-settings.module.scss';

type Props = {
    settings?: CustomSettingValueContract[];
    updateSetting: (setting_id: string, value: string) => void;
};

export function CustomSettings({ settings = [], updateSetting }: Props) {
    const groupedSettings = Object.entries(
        settings.reduce<Record<string, typeof settings>>((acc, item) => {
            const category = item.category;
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
                <Flex key={category} vertical className={styles.container}>
                    <Typography.Title level={3}>{category}</Typography.Title>
                    <Space direction="vertical">
                        {categorySettings.map((setting) => (
                            <Card key={setting.id} size="small">
                                <SettingsCardHeader
                                    isDefault={setting.is_default}
                                    resetToDefault={() => console.log('Set to default')}
                                />

                                <Typography.Title level={4}>{setting.name}</Typography.Title>
                                <Typography.Text type="secondary">{setting.tooltip}</Typography.Text>

                                <SettingsForm
                                    setting={setting}
                                    initialValue={setting.value}
                                    updateSetting={updateSetting}
                                />
                            </Card>
                        ))}
                    </Space>
                    {groupedSettings.length - 1 != index && <Divider />}
                </Flex>
            ))}
        </Flex>
    );
}
