import { Button, Form, FormInstance, FormProps, Input, Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import {
    useGetDataProductByIdQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { DataOutputConfiguration, DataOutputCreate, DataOutputCreateFormSchema, GlueDataOutput, S3DataOutput, S3DataOutputContract } from '@/types/data-output';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { Component, MutableRefObject, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { CustomDropdownItemProps } from '@/types/shared';


type Props = {
    mode: 'create';
    dataProductId: string;
    external_id: string|undefined;
    form: FormInstance<DataOutputCreateFormSchema&DataOutputConfiguration>;
};

export function S3DataOutputForm({ form, mode, dataProductId, external_id }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [configurationForm, setConfigurationForm] = useState<Element | null>();
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps<DataPlatforms> | undefined>(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps<DataPlatforms> | undefined>(undefined);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId);

    const buckets = ["datalake", "ingress"] // TODO Fetch from AWS platform settings;
    const bucketOptions = buckets.map((bucket) => ({ label: bucket, value: bucket })); //TODO
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const dataProductNameValue: string = Form.useWatch('temp_prefix', form);
    const canFillInForm = mode === 'create';
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const isLoading = isCreating || isCreating || isFetchingInitialValues;
    const onCancel = () => {
        form.resetFields();
    }

    const onSubmitFailed: FormProps<DataOutputConfiguration>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };
    useEffect(() => {
        if (dataProductNameValue) {
            form.setFieldsValue({ prefix: external_id + "/" + generateExternalIdFromName(dataProductNameValue)});
        } else {
            form.setFieldsValue({ prefix: external_id + "/"});
        }

    }, [dataProductNameValue]);

    // TODO form is not really interactive?

    return (
        <div>
                    <Form.Item<S3DataOutput>
                        name={'bucket'}
                        label={t('Bucket')}
                        rules={[
                            {
                                required: true,
                                message: t('The name of the S3 bucket to link the data output to'),
                            },
                        ]}
                    >
                        <Select
                            //loading={isFetchingDataProductTypes}
                            allowClear
                            showSearch
                            options={bucketOptions}
                            //filterOption={selectFilterOptionByLabelAndValue}
                        />
                    </Form.Item>
                    <Form.Item<S3DataOutput&{temp_prefix: string}>
                        name={'temp_prefix'}
                        label={t('Prefix')}
                        tooltip={t('The name of the prefix to give write access to')}
                        rules={[
                            {
                                required: true,
                                message: t('Please input the prefix of this data output'),
                            },
                        ]}
                    >
                        <Input/>
                    </Form.Item>
                    <Form.Item<S3DataOutput>
                        required
                        name={'prefix'}
                        label={t('Resulting prefix')}
                        tooltip={t('The path on s3 you can access through this data output')}
                    >
                        <Input disabled />
                    </Form.Item>
                    {/* <Form.Item<S3DataOutput>
                        required
                        name={'account_id'}
                        label={t('Account ID')}
                        tooltip={t('The AWS account ID the bucket is in')}
                    >
                        <Input/>
                    </Form.Item>
                    <Form.Item<S3DataOutput>
                        required
                        name={'kms_key'}
                        label={t('KMS Key')}
                        tooltip={t('KMS Key used to encrypt the data written to this data output')}
                    >
                        <Input/>
                    </Form.Item> */}
        </div>
    )
};
