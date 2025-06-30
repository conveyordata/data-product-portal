import { Form, type FormInstance, Input } from 'antd';
import type React from 'react';
import { useEffect } from 'react';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';

import { configurationFieldName } from './configuration-field-name';
import { ConfigurationFormItem } from './output-configuration-form-item';

type Props = {
    form: FormInstance;
    type: string;
    resultLabel: string;
    resultTooltip: string;
    children: React.ReactNode;
};

export function ConfigurationSubForm({ form, type, resultLabel, resultTooltip, children }: Props) {
    const configurationType = type;

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
