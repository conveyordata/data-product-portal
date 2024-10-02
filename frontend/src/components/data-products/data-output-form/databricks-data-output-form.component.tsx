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
    // const navigate = useNavigate();
    // const [configurationForm, setConfigurationForm] = useState<Element | null>();
    // const [selectedDataPlatform, setSelectedDataPlatform] = useState<
    //     CustomDropdownItemProps<DataPlatforms> | undefined
    // >(undefined);
    // const [selectedConfiguration, setSelectedConfiguration] = useState<
    //     CustomDropdownItemProps<DataPlatforms> | undefined
    // >(undefined);
    // const { data: _, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(dataProductId);

    let databaseOptions = (identifiers ?? []).map((database) => ({ label: database, value: database }));
    // const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    // const canFillInForm = mode === 'create';
    // const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    // const isLoading = isCreating || isCreating || isFetchingInitialValues;
    // const onCancel = () => {
    //     form.resetFields();
    // };

    // const onSubmitFailed: FormProps<DataOutputConfiguration>['onFinishFailed'] = () => {
    //     dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    // };

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
                name={'database'}
                label={t('Databricks database')}
                tooltip={t('The name of the Databricks database to link the data output to')}
                //hidden={!sourceAligned}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Databricks database for this data output'),
                    },
                ]}
            >
                <Select
                    //loading={isFetchingDataProductTypes}
                    allowClear
                    showSearch
                    mode='tags'
                    disabled={!sourceAligned}
                    onChange={value => {
                        // update data only when select one item or clear action
                        if (value.length > 0) {
                            form.setFieldsValue({ database: value[0] });
                        }
                    }}
                    maxCount={1}
                    options={databaseOptions}
                    //filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            <Form.Item<DatabricksDataOutput & { temp_suffix: string }>
                name={'database_suffix'}
                label={t('Database suffix')}
                tooltip={t('The suffix of the Databricks database to link the data output to')}
            >
                <Select
                    //loading={isFetchingDataProductTypes}
                    allowClear
                    maxCount={1}
                    showSearch
                    mode='tags'
                    options={[]} // TODO
                    onChange={value => {
                        // update data only when select one item or clear action
                        if (value.length > 0) {
                            form.setFieldsValue({ database_suffix: value[0] });
                        }
                    }}

                    //filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            <Form.Item<DatabricksDataOutput>
                required
                name={'table'}
                label={t('Table')}
                tooltip={t('The table that your data output can access')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the table this data output can access'),
                    },
                    {
                        required: true,
                        message: t('Please input the suffix of the Databricks database for this data output'),
                    },
                ]}
            >
                <Input/>
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
