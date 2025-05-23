import { Checkbox, Form, FormInstance, Input, Select } from 'antd';
import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputConfiguration, DataOutputCreateFormSchema, RedshiftDataOutput } from '@/types/data-output';

type Props = {
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    namespace: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function RedshiftDataOutputForm({ form, identifiers, namespace, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch('entire_schema', form);
    const databaseOptionsRef = useRef((identifiers ?? []).map((database) => ({ label: database, value: database })));
    const databaseValue = Form.useWatch('database', form);
    const schemaValue = Form.useWatch('schema', form);
    const tableValue = Form.useWatch('table', form);

    useEffect(() => {
        let databaseOptionsList = identifiers;
        if (!sourceAligned) {
            databaseOptionsList = [namespace];
            form.setFieldsValue({ database: namespace });
        } else {
            form.setFieldsValue({ database: undefined });
        }
        databaseOptionsRef.current = (databaseOptionsList ?? []).map((database) => ({
            label: database,
            value: database,
        }));
    }, [sourceAligned, identifiers, namespace, form]);

    useEffect(() => {
        let result = databaseValue;
        if (databaseValue) {
            if (schemaValue) {
                result += `__${schemaValue}`;
            }
            if (entireSchema) {
                result += '.*';
            } else if (tableValue) {
                result += `.${tableValue}`;
            }
        } else {
            result = '';
        }

        form.setFieldsValue({ result: result });
    }, [databaseValue, sourceAligned, schemaValue, tableValue, entireSchema, form]);

    return (
        <div>
            <Form.Item<RedshiftDataOutput>
                name={'database'}
                label={t('Schema')}
                tooltip={t('The name of the Redshift schema to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Redshift schema for this data output'),
                    },
                ]}
            >
                <Select
                    allowClear
                    showSearch
                    mode="tags"
                    disabled={!sourceAligned}
                    onChange={(value) => {
                        if (value.length > 0) {
                            form.setFieldsValue({ database: value[0] });
                        }
                    }}
                    maxCount={1}
                    options={databaseOptionsRef.current}
                />
            </Form.Item>
            <Form.Item<RedshiftDataOutput & { temp_suffix: string }>
                name={'schema'}
                label={t('Schema suffix')}
                tooltip={t('The suffix of the Redshift schema to link the data output to')}
            >
                <Input />
            </Form.Item>
            <Form.Item name={'entire_schema'} valuePropName="checked" initialValue={true}>
                <Checkbox defaultChecked={true}>{t('Include entire schema')}</Checkbox>
            </Form.Item>
            <Form.Item<RedshiftDataOutput>
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
            </Form.Item>
            <Form.Item<RedshiftDataOutput & { result: string }>
                required
                name={'result'}
                label={t('Resulting schema and table')}
                tooltip={t('The schema on Redshift you can access through this data output')}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
