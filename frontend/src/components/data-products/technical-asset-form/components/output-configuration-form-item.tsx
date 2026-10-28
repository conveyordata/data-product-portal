import { Form, type FormItemProps } from 'antd';

import { configurationFieldName } from './configuration-field-name';

export function ConfigurationFormItem({ name, ...restProps }: FormItemProps) {
    return <Form.Item name={configurationFieldName(name)} {...restProps} />;
}
