import { Checkbox, Form, type FormInstance, Input, Select } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import type { DataOutputCreateFormSchema } from '@/types/data-output';
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

export function GlueDataOutputForm({ form, identifiers = [], namespace, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch('entire_schema', form);

    const databaseOptions = (sourceAligned ? identifiers : [namespace]).map((database) => ({
        label: database,
        value: database,
    }));

    useEffect(() => {
        if (!sourceAligned) {
            form.setFieldValue(configurationFieldName('database'), namespace);
        } else {
            form.setFieldValue(configurationFieldName('database'), undefined);
        }
    }, [namespace, form, sourceAligned]);

    return (
        <ConfigurationSubForm
            form={form}
            platform={DataPlatforms.Glue}
            resultLabel={t('Resulting database and schema')}
            resultTooltip={t('The database and schema on Glue you can access through this data output')}
        >
            <ConfigurationFormItem
                name={'database'}
                label={t('Database')}
                tooltip={t('The name of the Glue database to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Glue database for this data output'),
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
                    options={databaseOptions}
                />
            </ConfigurationFormItem>
            <ConfigurationFormItem
                name={'database_suffix'}
                label={t('Database suffix')}
                tooltip={t('The suffix of the Glue database to link the data output to')}
            >
                <Input />
            </ConfigurationFormItem>
            <Form.Item name={'entire_schema'} valuePropName="checked" initialValue={true}>
                <Checkbox>{t('Include entire schema')}</Checkbox>
            </Form.Item>
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
