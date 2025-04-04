import { Checkbox, Form, FormInstance, Input, Select } from 'antd';
import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputConfiguration, DataOutputCreateFormSchema, SnowflakeDataOutput } from '@/types/data-output';

type Props = {
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    namespace: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function SnowflakeDataOutputForm({ form, identifiers, namespace, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireDatabase = Form.useWatch('entire_database', form);
    const databaseValue = Form.useWatch('database', form);
    const schemaValue = Form.useWatch('schema', form);
    const tableValue = Form.useWatch('table', form);

    const databaseOptions = useRef((identifiers ?? []).map((database) => ({ label: database, value: database })));

    useEffect(() => {
        let databaseOptionsList = identifiers; //TODO
        if (!sourceAligned) {
            databaseOptionsList = [namespace];
            form.setFieldsValue({ database: namespace });
        } else {
            form.setFieldsValue({ database: undefined });
        }
        databaseOptions.current = (databaseOptionsList ?? []).map((database) => ({ label: database, value: database }));
    }, [namespace, form, identifiers, sourceAligned]);

    useEffect(() => {
        let result = databaseValue;
        if (databaseValue) {
            if (schemaValue) {
                result += `__${schemaValue}`;
            }
            if (entireDatabase) {
                result += '.*';
            } else if (tableValue) {
                result += `.${tableValue}`;
            }
        } else {
            result = '';
        }

        form.setFieldsValue({ result: result });
    }, [databaseValue, sourceAligned, schemaValue, tableValue, entireDatabase, form]);

    return (
        <div>
            <Form.Item<SnowflakeDataOutput>
                name={'database'}
                label={t('Schema')}
                tooltip={t('The name of the Snowflake schema to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Snowflake schema for this data output'),
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
                    options={databaseOptions.current}
                />
            </Form.Item>
            <Form.Item<SnowflakeDataOutput & { temp_suffix: string }>
                name={'schema'}
                label={t('Schema suffix')}
                tooltip={t('The suffix of the Snowflake schema to link the data output to')}
            >
                <Input />
            </Form.Item>
            <Form.Item name={'entire_database'} valuePropName="checked" initialValue={true}>
                <Checkbox defaultChecked={true}>{t('Include entire database')}</Checkbox>
            </Form.Item>
            <Form.Item<SnowflakeDataOutput>
                required
                name={'table'}
                hidden={entireDatabase}
                label={t('Table')}
                tooltip={t('The table that your data output can access')}
                rules={[
                    {
                        required: !entireDatabase,
                        message: t('Please input the table this data output can access'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<SnowflakeDataOutput & { result: string }>
                required
                name={'result'}
                label={t('Resulting schema and table')}
                tooltip={t('The schema on Snowflake you can access through this data output')}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
