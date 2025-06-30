import type { FormInstance } from 'antd';
import { Checkbox, Input, Select } from 'antd';
import yaml from 'js-yaml';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDataOutputConfigQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import type { DataOutputCreateFormSchema, OutputConfig } from '@/types/data-output';
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
    let config: OutputConfig | undefined;
    if (config_yaml) {
        try {
            const parsed = yaml.load(config_yaml) as Record<string, OutputConfig>;
            config = parsed[Object.keys(parsed)[0]];
        } catch (_error) {
            config = undefined;
        }
    }

    useEffect(() => {
        config?.fields.forEach((field) => {
            if (field.default !== undefined) {
                console.log(field.default, field.name);
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
                // Skip field if hidden
                if (field.hidden) {
                    return null;
                }
                // Skip field if depends_on is set and that value is true
                if (field.depends_on && form.getFieldValue(configurationFieldName(field.depends_on)) === true) {
                    return null;
                }

                // const fieldName = configurationFieldName(field.name);
                const isRequired = !!field.required;

                const rules = isRequired ? [{ required: true, message: t(`Field "${field.name}" is required`) }] : [];
                const disabled = field.consumer_aligned_locked && !sourceAligned;
                if (disabled) {
                    form.setFieldValue(configurationFieldName(field.name), namespace);
                }
                const sharedProps = {
                    name: field.name,
                    label: t(field.label ?? field.name),
                    rules,
                    tooltip: field.tooltip ? t(field.tooltip) : undefined,
                };

                //      useEffect(() => {
                // -        if (!sourceAligned) {
                // -            form.setFieldValue(configurationFieldName('catalog'), namespace);
                // -        } else {
                // -            form.setFieldValue(configurationFieldName('catalog'), undefined);
                // -        }
                // -    }, [namespace, form, sourceAligned]);

                switch (field.type) {
                    case 'string':
                        return (
                            <ConfigurationFormItem required={field.required} key={field.name} {...sharedProps}>
                                <Input disabled={disabled} />
                            </ConfigurationFormItem>
                        );
                    case 'select':
                        return (
                            <ConfigurationFormItem required={field.required} key={field.name} {...sharedProps}>
                                <Select disabled={disabled} allowClear showSearch options={options} />
                            </ConfigurationFormItem>
                        );
                    case 'boolean':
                        return (
                            <ConfigurationFormItem
                                key={field.name}
                                required={field.required}
                                name={field.name}
                                valuePropName="checked"
                                initialValue={field.default || false}
                            >
                                <Checkbox disabled={disabled}>{t(field.label ?? field.name)}</Checkbox>
                            </ConfigurationFormItem>
                        );
                    default:
                        return null;
                }
            })}
        </ConfigurationSubForm>
    );
}
