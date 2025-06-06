import { Form, type FormInstance, Input } from 'antd';
import type React from 'react';
import { useEffect } from 'react';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type { DataPlatform } from '@/types/data-platform';
import { DataPlatformDataOutputConfigurationMap } from '@/types/data-platform/data-platform';

import { configurationFieldName } from './configuration-field-name';
import { ConfigurationFormItem } from './output-configuration-form-item';

type Props = {
    form: FormInstance;
    platform: DataPlatform;
    resultLabel: string;
    resultTooltip: string;
    children: React.ReactNode;
};

export function ConfigurationSubForm({ form, platform, resultLabel, resultTooltip, children }: Props) {
    const configurationType = DataPlatformDataOutputConfigurationMap.get(platform)?.toString();

    if (!configurationType) {
        const errorMessage = 'Data output not configured correctly';
        dispatchMessage({ content: errorMessage, type: 'error' });
    }

    useEffect(() => {
        form.setFieldValue(configurationFieldName('configuration_type'), configurationType);
    }, [form, configurationType]);

    return (
        <div>
            <ConfigurationFormItem name={'configuration_type'} hidden required>
                <Input />
            </ConfigurationFormItem>
            {children}
            <Form.Item name={'result'} label={resultLabel} tooltip={resultTooltip}>
                <Input disabled />
            </Form.Item>
        </div>
    );
}
