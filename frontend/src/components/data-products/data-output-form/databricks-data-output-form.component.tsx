import { Checkbox, Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputConfiguration, DataOutputCreateFormSchema, DatabricksDataOutput } from '@/types/data-output';
import { useEffect } from 'react';

type Props = {
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    external_id: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function DatabricksDataOutputForm({ form, identifiers, external_id, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch('entire_schema', form);
    let databaseOptions = (identifiers ?? []).map((database) => ({ label: database, value: database }));
    const databaseValue = Form.useWatch('schema', form);
    const suffixValue = Form.useWatch('schema_suffix', form);
    const tableValue = Form.useWatch('table', form);
    useEffect(() => {
        let databaseOptionsList = identifiers //TODO
        if (!sourceAligned) {
            databaseOptionsList = [external_id]
            form.setFieldsValue({ schema: external_id});
        } else {
            form.setFieldsValue({schema: undefined})
        }
        databaseOptions = (databaseOptionsList ?? []).map((database) => ({ label: database, value: database }));
    }, [sourceAligned]);


    useEffect(() => {
        let result = databaseValue;
        if (databaseValue){
            if (suffixValue) {
                result += `__${suffixValue}`;
            }
            if (entireSchema) {
                result += '.*'
            }
            else if (tableValue) {
                result += `.${tableValue}`;
            }
        } else {
            result = ""
        }

        form.setFieldsValue({ result: result });
    }, [databaseValue, sourceAligned, suffixValue, tableValue, entireSchema]);

    return (
        <div>
            <Form.Item<DatabricksDataOutput>
                name={'schema'}
                label={t('Databricks schema')}
                tooltip={t('The name of the Databricks schema to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Databricks schema for this data output'),
                    },
                ]}
            >
                <Select
                    allowClear
                    showSearch
                    mode='tags'
                    disabled={!sourceAligned}
                    onChange={value => {
                        if (value.length > 0) {
                            form.setFieldsValue({ schema: value[0] });
                        }
                    }}
                    maxCount={1}
                    options={databaseOptions}
                />
            </Form.Item>
            <Form.Item<DatabricksDataOutput & { temp_suffix: string }>
                name={'schema_suffix'}
                label={t('Schema suffix')}
                tooltip={t('The suffix of the Databricks schema to link the data output to')}
            >
                <Input/>
            </Form.Item>
            <Form.Item
                name={'entire_schema'} valuePropName="checked" initialValue={true}
            >
                <Checkbox defaultChecked={true}>{t('Include entire schema')}</Checkbox>
            </Form.Item>
            <Form.Item<DatabricksDataOutput>
                required
                name={'table'}
                hidden={entireSchema}
                label={t('Table')}
                tooltip={t('The table that your data output can access')}
                rules={[
                    {
                        required: !entireSchema,
                        message: t('Please input the table this data output can access'),
                    }
                ]}
            >
                <Input/>
            </Form.Item>
            <Form.Item<DatabricksDataOutput & {result: string}>
                required
                name={'result'}
                label={t('Resulting database and schema')}
                tooltip={t('The schema on Databricks you can access through this data output')}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
