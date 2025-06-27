import type { FormInstance } from 'antd';
import { Checkbox, Form, Input, Select } from 'antd';
import yaml from 'js-yaml';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDataOutputConfigQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import type { DataOutputConfig, DataOutputCreateFormSchema } from '@/types/data-output';
import type { DataPlatform } from '@/types/data-platform';
import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    form: FormInstance<DataOutputCreateFormSchema>;
    namespace: string;
    sourceAligned: boolean;
    identifiers?: string[];
    platform: DataPlatform;
};

export function DynamicDataOutputForm({ form, namespace, sourceAligned, identifiers = [], platform }: Props) {
    const { t } = useTranslation();
    const { data: config_yaml } = useGetDataOutputConfigQuery(platform);
    const options = identifiers.map((id) => ({ label: id, value: id }));

    let config: DataOutputConfig | undefined;
    if (config_yaml) {
        try {
            const parsed = yaml.load(config_yaml) as Record<string, DataOutputConfig>;
            config = parsed[Object.keys(parsed)[0]];
        } catch (_error) {
            config = undefined;
        }
    }

    useEffect(() => {
        config?.fields.forEach((field) => {
            if (field.default !== undefined) {
                const fullName = configurationFieldName(field.name);
                const current = form.getFieldValue(fullName);
                if (current === undefined) {
                    form.setFieldValue(fullName, field.default);
                }
            }
        });
    }, [form, config?.fields]);

    return (
        <ConfigurationSubForm
            form={form}
            platform={platform}
            resultLabel={t('Result')}
            resultTooltip={t('The resulting configuration')}
        >
            {config?.fields.map((field) => {
                // const fieldName = configurationFieldName(field.name);
                const isRequired = !!field.required;

                const rules = isRequired ? [{ required: true, message: t(`Field "${field.name}" is required`) }] : [];

                const sharedProps = {
                    name: field.name,
                    label: t(field.name),
                    rules,
                };

                switch (field.type) {
                    case 'string':
                        return (
                            <ConfigurationFormItem key={field.name} {...sharedProps}>
                                <Input />
                            </ConfigurationFormItem>
                        );
                    case 'select':
                        return (
                            <ConfigurationFormItem key={field.name} {...sharedProps}>
                                <Select allowClear showSearch options={options} />
                            </ConfigurationFormItem>
                        );
                    case 'boolean':
                        return (
                            <ConfigurationFormItem
                                key={field.name}
                                name={field.name}
                                valuePropName="checked"
                                initialValue={field.default || false}
                            >
                                <Checkbox>{t(field.name)}</Checkbox>
                            </ConfigurationFormItem>
                        );
                    default:
                        return null;
                }
            })}
        </ConfigurationSubForm>
    );
}
