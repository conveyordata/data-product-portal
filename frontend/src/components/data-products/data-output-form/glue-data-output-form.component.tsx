import { Checkbox, Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputConfiguration, DataOutputCreateFormSchema, GlueDataOutput } from '@/types/data-output';
import { useEffect } from 'react';

type Props = {
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    external_id: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function GlueDataOutputForm({ form, identifiers, external_id, sourceAligned }: Props) {
    const { t } = useTranslation();
    const entireSchema = Form.useWatch('entire_schema', form);
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
            <Form.Item<GlueDataOutput>
                name={'database'}
                label={t('Glue database')}
                tooltip={t('The name of the Glue database to link the data output to')}
                //hidden={!sourceAligned}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Glue database for this data output'),
                    },
                ]}
            >
                <Select
                    //loading={isFetchingDataProductTypes}
                    allowClear
                    showSearch
                    mode='tags'
                    onChange={value => {
                        // update data only when select one item or clear action
                        if (value.length > 0) {
                            form.setFieldsValue({ database: value[0] });
                        }
                    }}
                    disabled={!sourceAligned}
                    maxCount={1}
                    options={databaseOptions}
                    //filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            <Form.Item<GlueDataOutput & { temp_suffix: string }>
                name={'database_suffix'}
                label={t('Database suffix')}
                tooltip={t('The suffix of the Glue database to link the data output to')}
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
            <Form.Item
                name={'entire_schema'} valuePropName="checked" initialValue={true}
            >
                <Checkbox defaultChecked={true}>{t('Include entire schema')}</Checkbox>
            </Form.Item>
            <Form.Item<GlueDataOutput>
                    required
                    hidden={true}
                    name={'configuration_type'}
                    initialValue={'GlueDataOutput'}
                ></Form.Item>
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
                <Input/>
            </Form.Item>
            <Form.Item<GlueDataOutput>
                required
                hidden={true}
                name={'database_suffix'}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
