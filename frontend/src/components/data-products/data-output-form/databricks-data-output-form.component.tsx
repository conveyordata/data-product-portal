import { Checkbox, Form, FormInstance, Input, Select } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputCreateFormSchema } from '@/types/data-output';
import { DataPlatforms } from '@/types/data-platform';

import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    sourceAligned: boolean;
    identifiers?: string[];
    namespace: string;
    form: FormInstance<DataOutputCreateFormSchema>;
};

export function DatabricksDataOutputForm({ form, identifiers = [], namespace, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch(configurationFieldName('entire_schema'), form);

    const catalogOptions = (sourceAligned ? identifiers : [namespace]).map((catalog) => ({
        label: catalog,
        value: catalog,
    }));

    useEffect(() => {
        if (!sourceAligned) {
            form.setFieldValue(configurationFieldName('catalog'), namespace);
        } else {
            form.setFieldValue(configurationFieldName('catalog'), undefined);
        }
    }, [namespace, form, sourceAligned]);

    return (
        <ConfigurationSubForm
            form={form}
            platform={DataPlatforms.Databricks}
            resultLabel={t('Resulting catalog and schema')}
            resultTooltip={t('The schema on Databricks you can access through this data output')}
        >
            <ConfigurationFormItem
                name={'catalog'}
                label={t('Catalog')}
                tooltip={t('The name of the Databricks catalog to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Databricks catalog for this data output'),
                    },
                ]}
                normalize={(value: string | string[]) => {
                    return Array.isArray(value) ? value[0] : value;
                }}
            >
                <Select
                    allowClear
                    showSearch
                    mode="tags"
                    disabled={!sourceAligned}
                    maxCount={1}
                    options={catalogOptions}
                />
            </ConfigurationFormItem>
            <ConfigurationFormItem
                name={'schema'}
                label={t('Schema')}
                tooltip={t('The schema to link the data output to')}
            >
                <Input />
            </ConfigurationFormItem>
            <ConfigurationFormItem name={'entire_schema'} valuePropName="checked" initialValue={true}>
                <Checkbox>{t('Include entire schema')}</Checkbox>
            </ConfigurationFormItem>
            <ConfigurationFormItem
                required
                name={'table'}
                hidden={entireSchema}
                label={t('Table')}
                tooltip={t('The table that your data output can access')}
                rules={[
                    {
                        required: !entireSchema,
                        message: t('Please input the table this data output can access'),
                    },
                ]}
            >
                <Input />
            </ConfigurationFormItem>
        </ConfigurationSubForm>
    );
}
