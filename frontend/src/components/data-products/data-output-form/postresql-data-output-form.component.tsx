import { Checkbox, Form, type FormInstance, Input, Select } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import type { DataOutputConfiguration, DataOutputCreateFormSchema } from '@/types/data-output';
import { DataPlatforms } from '@/types/data-platform';

import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    sourceAligned: boolean;
    identifiers?: string[];
    namespace: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function PostgreSQLDataOutputForm({ form, identifiers = [], namespace, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch(configurationFieldName('entire_schema'), form);

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
            platform={DataPlatforms.PostgreSQL}
            resultLabel={t('Resulting database and schema')}
            resultTooltip={t('The schema on PostgeSQL you can access through this technical asset')}
        >
            <ConfigurationFormItem
                name={'database'}
                label={t('Database')}
                tooltip={t('The name of the PostgeSQL database to link the technical asset to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the PostgeSQL database for this technical asset'),
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
                name={'schema'}
                label={t('Schema')}
                tooltip={t('The PostgeSQL schema to link the technical asset to')}
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
                tooltip={t('The table that your technical asset can access')}
                rules={[
                    {
                        required: !entireSchema,
                        message: t('Please input the table this technical asset can access'),
                    },
                ]}
            >
                <Input />
            </ConfigurationFormItem>
        </ConfigurationSubForm>
    );
}
