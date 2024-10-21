import { Form, FormInstance, Input, Select } from 'antd';
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
    let databaseOptions = (identifiers ?? []).map((database) => ({ label: database, value: database }));

    useEffect(() => {
        let databaseOptionsList = identifiers //TODO
        if (!sourceAligned) {
            databaseOptionsList = [external_id]
            form.setFieldsValue({ database: external_id});
        } else {
            form.setFieldsValue({database: undefined})
        }
        databaseOptions = (databaseOptionsList ?? []).map((database) => ({ label: database, value: database }));
    }, [sourceAligned]);

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
                            form.setFieldsValue({ database: value[0] });
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
                <Select
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
                />
            </Form.Item>
            <Form.Item<DatabricksDataOutput>
                required
                hidden={true}
                name={'configuration_type'}
                initialValue={"DatabricksDataOutput"}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
