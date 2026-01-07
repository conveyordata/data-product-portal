import { Checkbox, Form, type FormInstance, Input, Select } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import type { DataOutputCreateFormSchema } from '@/types/data-output';
import { DataPlatforms } from '@/types/data-platform';

import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    form: FormInstance<DataOutputCreateFormSchema>;
    namespace: string;
    identifiers?: string[];
    sourceAligned: boolean;
    platform?: DataPlatforms;
    uiMetadataGroups: UIElementMetadata[];
    resultLabel?: string;
    resultTooltip?: string;
};

export function GenericDataOutputForm({
    form,
    namespace,
    identifiers = [],
    sourceAligned,
    uiMetadataGroups,
    platform = DataPlatforms.S3,
    resultLabel,
    resultTooltip,
}: Props) {
    const { t } = useTranslation();
    const uiMetadata = uiMetadataGroups as UIElementMetadata[] | undefined;

    // Get all unique field names that have dependencies
    const fieldsToWatch = Array.from(
        new Set((uiMetadata || []).filter((field) => field.depends_on).map((field) => field.depends_on!.fieldName)),
    );

    // Watch each field individually - hooks must be called unconditionally
    // We watch all potential fields that might be dependencies
    const entireSchema = Form.useWatch(configurationFieldName('entire_schema'), form);

    // Build the watched fields map
    const watchedFields: Record<string, any> = {
        entire_schema: entireSchema,
    };

    // Auto-populate fields based on sourceAligned and namespace
    useEffect(() => {
        uiMetadata?.forEach((field) => {
            // Handle suffix field
            if (field.name === 'suffix') {
                form.setFieldValue(configurationFieldName('suffix'), sourceAligned ? '' : namespace);
            }

            // Handle fields that should auto-populate from namespace when not source-aligned
            if (field.useNamespaceWhenNotSourceAligned) {
                if (!sourceAligned) {
                    form.setFieldValue(configurationFieldName(field.name), namespace);
                } else {
                    form.setFieldValue(configurationFieldName(field.name), undefined);
                }
            }
        });
    }, [form, sourceAligned, namespace, uiMetadata]);

    if (!uiMetadata) {
        return null;
    }

    const renderFormField = (fieldMetadata: UIElementMetadata) => {
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
            select_mode,
            max_count,
            disabled,
            use_namespace_when_not_source_aligned,
            normalize_array,
        } = fieldMetadata;

        // Check if field should be hidden based on dependencies
        let isHidden = hidden;
        if (depends_on) {
            const dependentValue = watchedFields[depends_on.fieldName];
            isHidden = dependentValue !== depends_on.value;
        }

        // Build validation rules
        const rules: any[] = [];
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
        let selectOptions;
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
        let inputComponent;
        switch (type) {
            case 'checkbox':
                inputComponent = <Checkbox>{t(label)}</Checkbox>;
                break;

            case 'select':
                inputComponent = (
                    <Select
                        allowClear
                        showSearch
                        mode={select_mode}
                        maxCount={max_count}
                        disabled={isDisabled}
                        options={selectOptions}
                    />
                );
                break;

            case 'string':
            default:
                inputComponent = <Input />;
                break;
        }
        console.log(fieldMetadata);
        return (
            <ConfigurationFormItem
                key={name}
                name={name}
                label={type === 'checkbox' ? undefined : t(label)}
                tooltip={tooltip ? t(tooltip) : undefined}
                rules={rules}
                hidden={isHidden}
                valuePropName={value_prop_name}
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
            platform={platform}
            resultLabel={resultLabel ? t(resultLabel) : t('Resulting path')}
            resultTooltip={resultTooltip ? t(resultTooltip) : t('The path you can access through this technical asset')}
        >
            {uiMetadata.map(renderFormField)}
        </ConfigurationSubForm>
    );
}
