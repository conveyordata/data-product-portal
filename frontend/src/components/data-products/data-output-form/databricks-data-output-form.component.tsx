import { Checkbox, Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputConfiguration, DataOutputCreateFormSchema, DatabricksDataOutput } from '@/types/data-output';
import { useEffect, useRef } from 'react';

type Props = {
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    external_id: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function DatabricksDataOutputForm({ form, identifiers, external_id, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireCatalog = Form.useWatch('entire_catalog', form);
    const catalogValue = Form.useWatch('catalog', form);
    const schemaValue = Form.useWatch('schema', form);
    const tableValue = Form.useWatch('table', form);

    const catalogOptions = useRef((identifiers ?? []).map((catalog) => ({ label: catalog, value: catalog })));

    useEffect(() => {
        let catalogOptionsList = identifiers; //TODO
        if (!sourceAligned) {
            catalogOptionsList = [external_id];
            form.setFieldsValue({ catalog: external_id });
        } else {
            form.setFieldsValue({ catalog: undefined });
        }
        catalogOptions.current = (catalogOptionsList ?? []).map((catalog) => ({ label: catalog, value: catalog }));
    }, [external_id, form, identifiers, sourceAligned]);

    useEffect(() => {
        let result = catalogValue;
        if (catalogValue) {
            if (schemaValue) {
                result += `.${schemaValue}`;
            }
            if (entireCatalog) {
                result += '.*';
            } else if (tableValue) {
                result += `.${tableValue}`;
            }
        } else {
            result = '';
        }

        form.setFieldsValue({ result: result });
    }, [catalogValue, sourceAligned, schemaValue, tableValue, entireCatalog, form]);

    return (
        <div>
            <Form.Item<DatabricksDataOutput>
                name={'catalog'}
                label={t('Catalog')}
                tooltip={t('The name of the Databricks catalog to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Databricks catalog for this data output'),
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
                            form.setFieldsValue({ catalog: value[0] });
                        }
                    }}
                    maxCount={1}
                    options={catalogOptions.current}
                />
            </Form.Item>
            <Form.Item<DatabricksDataOutput & { temp_suffix: string }>
                name={'schema'}
                label={t('Schema')}
                tooltip={t('The schema to link the data output to')}
            >
                <Input />
            </Form.Item>
            <Form.Item name={'entire_catalog'} valuePropName="checked" initialValue={true}>
                <Checkbox defaultChecked={true}>{t('Include entire catalog')}</Checkbox>
            </Form.Item>
            <Form.Item<DatabricksDataOutput>
                required
                name={'table'}
                hidden={entireCatalog}
                label={t('Table')}
                tooltip={t('The table that your data output can access')}
                rules={[
                    {
                        required: !entireCatalog,
                        message: t('Please input the table this data output can access'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<DatabricksDataOutput & { result: string }>
                required
                name={'result'}
                label={t('Resulting catalog and schema')}
                tooltip={t('The schema on Databricks you can access through this data output')}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
