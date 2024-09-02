import { Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputConfiguration, DataOutputCreateFormSchema, GlueDataOutput } from '@/types/data-output';
import { useEffect } from 'react';
// import styles from './data-output-form.module.scss';
// import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
// import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
// import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
// import { Component, MutableRefObject, useEffect, useMemo, useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { createDataProductIdPath } from '@/types/navigation.ts';
// import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
// import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
// import { DataPlatform, DataPlatforms } from '@/types/data-platform';
// import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
// import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
// import { CustomDropdownItemProps } from '@/types/shared';

type Props = {
    sourceAligned: boolean;
    external_id: string | undefined;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function GlueDataOutputForm({ form, external_id, sourceAligned }: Props) {
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

    const database = ["hardcoded_dp_db"]
    const databases = ['dp1_db', 'dp2_db']; // TODO Fetch from AWS platform settings;
    let databaseOptions = databases.map((database) => ({ label: database, value: database })); //TODO
    // const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const dataProductNameValue: string = Form.useWatch('temp_prefix', form);
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
        let databaseOptionsList = databases //TODO
        if (!sourceAligned) {
            databaseOptionsList = database
            form.setFieldsValue({ glue_database: database[0]});
        } else {
            form.setFieldsValue({glue_database: undefined})
        }
        databaseOptions = databaseOptionsList.map((database) => ({ label: database, value: database }));
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
