import { Checkbox, Form, type FormInstance, Input, Select } from 'antd';
import { type ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { UiElementMetadata } from '@/store/api/services/generated/pluginsApi';
import type { DataOutputCreateFormSchema } from '@/types/data-output';
import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    form: FormInstance<DataOutputCreateFormSchema>;
    namespace: string;
    identifiers?: string[];
    sourceAligned: boolean;
    configurationType: string;
    uiMetadataGroups: UiElementMetadata[];
    resultLabel?: string;
    resultTooltip?: string;
};

export function GenericDataOutputForm({
    form,
    namespace,
    identifiers = [],
    sourceAligned,
    uiMetadataGroups,
    configurationType,
    resultLabel,
    resultTooltip,
}: Props) {
    const { t } = useTranslation();
    const uiMetadata = uiMetadataGroups as UiElementMetadata[] | undefined;

    // Watch each field individually - hooks must be called unconditionally
    // We watch all potential fields that might be dependencies
    const entireSchema = Form.useWatch(configurationFieldName('entire_schema'), form);

    // Build the watched fields map
    const watchedFields: Record<string, unknown> = {
        entire_schema: entireSchema,
    };

    // Auto-populate fields based on sourceAligned and namespace
    useEffect(() => {
        uiMetadata?.forEach((field) => {
            // Handle suffix field
            if (field.name === 'suffix') {
                form.setFields([
                    {
                        // biome-ignore lint: dynamic field names can't be statically typed at compile time.
                        name: configurationFieldName('suffix') as any,
                        value: sourceAligned ? '' : namespace,
                    },
                ]);
            }

            // Handle fields that should auto-populate from namespace when not source-aligned
            if (field.use_namespace_when_not_source_aligned) {
                form.setFields([
                    {
                        // biome-ignore lint: dynamic field names can't be statically typed at compile time.
                        name: configurationFieldName(field.name) as any,
                        value: !sourceAligned ? namespace : undefined,
                    },
                ]);
            }
        });
    }, [form, sourceAligned, namespace, uiMetadata]);

    if (!uiMetadata) {
        return null;
    }

    const renderFormField = (fieldMetadata: UiElementMetadata) => {
        const {
            name,
            label,
            type,
            required,
            tooltip,
            options,
            hidden,
            pattern,
            initial_value,
            value_prop_name,
            depends_on,
            max_count,
            disabled,
            use_namespace_when_not_source_aligned,
            normalize_array,
        } = fieldMetadata;

        // Check if field should be hidden based on dependencies
        let isHidden = hidden;
        if (depends_on) {
            const dependentValue = watchedFields[depends_on.field_name];
            isHidden = dependentValue !== depends_on.value;
        }

        // Build validation rules
        const rules: { required?: boolean; pattern?: RegExp; message?: string }[] = [];
        if (required && !isHidden) {
            rules.push({
                required: true,
                message: t(`Please input ${label.toLowerCase()}`),
            });
        }
        if (pattern) {
            rules.push({
                pattern: new RegExp(pattern),
                message: t(`Invalid format for ${label.toLowerCase()}`),
            });
        }

        // Build select options based on sourceAligned for fields that use namespace
        let selectOptions: { label: string; value: string }[] = [];
        if (type === 'select') {
            if (use_namespace_when_not_source_aligned) {
                selectOptions = (sourceAligned ? identifiers : [namespace]).map((val) => ({
                    label: val,
                    value: val,
                }));
            } else {
                selectOptions = options?.values
                    ? options.values.map((val: string) => ({ label: val, value: val }))
                    : identifiers.map((id) => ({ label: id, value: id }));
            }
        }

        // Normalize function for array handling
        const normalize = normalize_array
            ? (value: string | string[]) => {
                  return Array.isArray(value) ? value[0] : value;
              }
            : undefined;

        // Determine if field should be disabled
        const isDisabled = disabled || (use_namespace_when_not_source_aligned && !sourceAligned);

        // Render the appropriate input component based on type
        let inputComponent: ReactElement;
        switch (type) {
            case 'checkbox':
                inputComponent = <Checkbox>{t(label)}</Checkbox>;
                break;

            case 'select':
                inputComponent = (
                    <Select
                        allowClear
                        showSearch
                        maxCount={max_count || undefined}
                        disabled={isDisabled ?? false}
                        options={selectOptions}
                    />
                );
                break;

            case 'string':
            default:
                inputComponent = <Input />;
                break;
        }
        return (
            <ConfigurationFormItem
                key={name}
                name={name}
                label={type === 'checkbox' ? undefined : t(label)}
                tooltip={tooltip ? t(tooltip) : undefined}
                rules={rules}
                hidden={isHidden ?? false}
                valuePropName={value_prop_name ?? (type === 'checkbox' ? 'checked' : 'value')}
                initialValue={initial_value}
                normalize={normalize}
                required={type !== 'checkbox' && required && !isHidden}
            >
                {inputComponent}
            </ConfigurationFormItem>
        );
    };

    return (
        <ConfigurationSubForm
            form={form}
            configurationType={configurationType}
            resultLabel={resultLabel ? t(resultLabel) : t('Resulting path')}
            resultTooltip={resultTooltip ? t(resultTooltip) : t('The path you can access through this technical asset')}
        >
            {uiMetadata.map(renderFormField)}
        </ConfigurationSubForm>
    );
}
