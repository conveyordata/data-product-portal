import { Form, FormInstance, Select } from 'antd';
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
    // const navigate = useNavigate();
    // const [configurationForm, setConfigurationForm] = useState<Element | null>();
    // const [selectedDataPlatform, setSelectedDataPlatform] = useState<
    //     CustomDropdownItemProps<DataPlatforms> | undefined
    // >(undefined);
    // const [selectedConfiguration, setSelectedConfiguration] = useState<
    //     CustomDropdownItemProps<DataPlatforms> | undefined
    // >(undefined);
    // const { data: _, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(dataProductId);

    let databaseOptions = identifiers?.map((database) => ({ label: database, value: database }));
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
            form.setFieldsValue({ glue_database: external_id});
        } else {
            form.setFieldsValue({glue_database: undefined})
        }
        databaseOptions = databaseOptionsList?.map((database) => ({ label: database, value: database }));
    }, [sourceAligned]);

    return (
        <div>
            <Form.Item<GlueDataOutput>
                name={'glue_database'}
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
                    disabled={!sourceAligned}
                    options={databaseOptions}
                    //filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            {/* <Form.Item<GlueDataOutput>
                name={'glue_database'}
                label={t('Glue database')}
                tooltip={t('The name of the Glue database to link the data output to')}
                //hidden={sourceAligned}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Glue database for this data output'),
                    },
                ]}
            >
                <Select
                    //loading={isFetchingDataProductTypes}
                    disabled={true}
                    options={databaseOptions}
                    //filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item> */}
            <Form.Item<GlueDataOutput>
                required
                name={'table_prefixes'}
                label={t('Table prefixes')}
                tooltip={t('The tables that your data output can access')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the tables this data output can access'),
                    },
                ]}
            >
                <Select tokenSeparators={[',']} placeholder={t('Provide table prefixes')} mode={'tags'} options={[]} />
            </Form.Item>
        </div>
    );
}
