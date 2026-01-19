import { Checkbox, Form, type FormInstance, Input, Select } from 'antd';
import type { Rule } from 'antd/es/form';
import type { BaseOptionType } from 'antd/es/select';
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
    sourceAligned: boolean;
    configurationType: string;
    uiMetadataGroups: UiElementMetadata[];
    resultLabel: string;
    resultTooltip: string;
};

export function DataOutputConfigurationForm({
    form,
    namespace,
    sourceAligned,
    uiMetadataGroups,
    configurationType,
    resultLabel,
    resultTooltip,
}: Props) {
    const { t } = useTranslation();
    const uiMetadata = uiMetadataGroups as UiElementMetadata[];

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
                form.setFieldValue(configurationFieldName('suffix'), sourceAligned ? '' : namespace);
            }

            // Handle fields that should auto-populate from namespace when not source-aligned
            if (field.use_namespace_when_not_source_aligned) {
                // biome-ignore lint: dynamic field names can't be statically typed at compile time.
                form.setFieldValue(configurationFieldName(field.name) as any, !sourceAligned ? namespace : undefined);
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
            hidden,
            depends_on,
            options,
            disabled,
            use_namespace_when_not_source_aligned,
            string,
            checkbox,
            select,
        } = fieldMetadata;

        // Check if field should be hidden based on dependencies
        let isHidden = hidden;

        // Depends on can have multiple dependencies
        if (depends_on) {
            for (const dep of depends_on) {
                const dependentValue = watchedFields[dep.field_name];
                if (dependentValue !== dep.value) {
                    isHidden = true;
                    break;
                }
                isHidden = false;
            }
        }

        // Build validation rules
        const rules: Rule[] = [];
        if (required && !isHidden) {
            rules.push({
                required: true,
                message: t(`Please input ${label.toLowerCase()}`),
            });
        }

        // Build select options based on sourceAligned for fields that use namespace
        let selectOptions: BaseOptionType[] = [];
        if (type === 'select') {
            selectOptions = options?.map((option) => ({ label: option.label, value: option.value.toString() })) ?? [];
            if (use_namespace_when_not_source_aligned && !sourceAligned) {
                selectOptions = [namespace].map((val) => ({
                    label: val,
                    value: val,
                }));
            } else {
                selectOptions =
                    options?.map((option) => ({ label: option.label, value: option.value.toString() })) ?? [];
            }
        }

        // Determine if field should be disabled
        const isDisabled = disabled || (use_namespace_when_not_source_aligned && !sourceAligned);

        // Render the appropriate input component based on type
        let inputComponent: ReactElement;
        switch (type) {
            case 'checkbox':
                inputComponent = <Checkbox>{label}</Checkbox>;
                break;

            case 'select':
                inputComponent = (
                    <Select
                        allowClear
                        showSearch
                        maxCount={select?.max_count || undefined}
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
                label={type === 'checkbox' ? undefined : label}
                tooltip={tooltip ?? undefined}
                rules={rules}
                hidden={isHidden ?? false}
                valuePropName={type === 'checkbox' ? 'checked' : 'value'}
                initialValue={
                    type === 'string'
                        ? string?.initial_value
                        : type === 'checkbox'
                          ? checkbox?.initial_value
                          : undefined
                }
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
            resultLabel={resultLabel}
            resultTooltip={resultTooltip}
        >
            {uiMetadata.map(renderFormField)}
        </ConfigurationSubForm>
    );
}
