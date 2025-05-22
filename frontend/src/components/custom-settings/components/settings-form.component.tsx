import { Form, Input, Select, Switch } from 'antd';
import { useDebouncedCallback } from 'use-debounce';

import { DataProductSettingContract } from '@/types/data-product-setting';

import styles from '../custom-settings.module.scss';

type Props = {
    setting: DataProductSettingContract;
    initialValue: string;
    updateSetting: (setting_id: string, value: string) => void;
};

export function SettingsForm({ setting, initialValue, updateSetting }: Props) {
    const inputField = (() => {
        switch (setting.type) {
            case 'checkbox':
                return <Switch />;
            case 'tags':
                return <Select allowClear={false} defaultActiveFirstOption mode="tags" />;
            case 'input':
                return <Input />;
        }
    })();

    const initial = (() => {
        switch (setting.type) {
            case 'checkbox':
                return initialValue === 'true';
            case 'tags':
                return initialValue !== '' ? initialValue.split(',') : [];
            case 'input':
                return initialValue;
        }
    })();

    const onValuesChangeDebounced = useDebouncedCallback(
        (changedValues) => updateSetting(setting.id, changedValues[setting.id].toString()),
        500,
    );

    return (
        <Form layout="vertical" className={styles.form} onValuesChange={onValuesChangeDebounced}>
            <Form.Item name={setting.id} initialValue={initial}>
                {inputField}
            </Form.Item>
        </Form>
    );
}
