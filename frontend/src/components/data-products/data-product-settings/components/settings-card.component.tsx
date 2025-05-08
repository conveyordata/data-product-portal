import { Card, Typography } from 'antd';

import { DataProductSettingContract } from '@/types/data-product-setting';

import { SettingsCardHeader } from './settings-card-header.component';
import { SettingsForm } from './settings-form.component';

type Props = {
    setting: DataProductSettingContract;
    value: string;
    isDefault: boolean;
    updateSetting: (setting_id: string, value: string) => void;
};

export function SettingsCard({ setting, value, isDefault, updateSetting }: Props) {
    return (
        <Card size="small">
            <SettingsCardHeader isDefault={isDefault} resetToDefault={() => console.log('Set to default')} />

            <Typography.Title level={4}>{setting.name}</Typography.Title>
            <Typography.Text type="secondary">{setting.tooltip}</Typography.Text>

            <SettingsForm setting={setting} initialValue={value} updateSetting={updateSetting} />
        </Card>
    );
}
