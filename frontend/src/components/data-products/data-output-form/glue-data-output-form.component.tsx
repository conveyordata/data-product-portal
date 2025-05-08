import { Checkbox, Form, type FormInstance, Input, Select } from 'antd';
import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import type { DataOutputConfiguration, DataOutputCreateFormSchema, GlueDataOutput } from '@/types/data-output';

type Props = {
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    namespace: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function GlueDataOutputForm({ form, identifiers, namespace, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch('entire_schema', form);
    const databaseValue = Form.useWatch('database', form);
    const suffixValue = Form.useWatch('database_suffix', form);
    const tableValue = Form.useWatch('table', form);

    const databaseOptions = useRef((identifiers ?? []).map((database) => ({ label: database, value: database })));

    useEffect(() => {
        let databaseOptionsList = identifiers;
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
            if (suffixValue) {
                result += `__${suffixValue}`;
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
    }, [databaseValue, sourceAligned, suffixValue, tableValue, entireSchema, form]);

    return (
        <div>
            <Form.Item<GlueDataOutput>
                name={'database'}
                label={t('Database')}
                tooltip={t('The name of the Glue database to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Glue database for this data output'),
                    },
                ]}
            >
                <Select
                    allowClear
                    showSearch
                    mode="tags"
                    onChange={(value) => {
                        if (value.length > 0) {
                            form.setFieldsValue({ database: value[0] });
                        }
                    }}
                    disabled={!sourceAligned}
                    maxCount={1}
                    options={databaseOptions.current}
                />
            </Form.Item>
            <Form.Item<GlueDataOutput & { temp_suffix: string }>
                name={'database_suffix'}
                label={t('Database suffix')}
                tooltip={t('The suffix of the Glue database to link the data output to')}
            >
                {/* <Select
                    allowClear
                    maxCount={1}
                    showSearch
                    mode='tags'
                    options={[]} // TODO
                    onChange={value => {
                        if (value.length > 0) {
                            form.setFieldsValue({ database_suffix: value[0] });
                        }
                    }}
                /> */}
                <Input />
            </Form.Item>
            <Form.Item name={'entire_schema'} valuePropName="checked" initialValue={true}>
                <Checkbox defaultChecked={true}>{t('Include entire schema')}</Checkbox>
            </Form.Item>
            <Form.Item<GlueDataOutput>
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
                    {
                        required: !entireSchema,
                        message: t('Please input the suffix of the Glue database for this data output'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<GlueDataOutput> required hidden={true} name={'database_suffix'}>
                <Input disabled />
            </Form.Item>
            <Form.Item<GlueDataOutput & { result: string }>
                required
                name={'result'}
                label={t('Resulting database and schema')}
                tooltip={t('The database and schema on Glue you can access through this data output')}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
