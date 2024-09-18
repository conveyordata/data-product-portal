import { Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    DataOutputConfiguration,
    DataOutputCreateFormSchema,
    S3DataOutput,
} from '@/types/data-output';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { useEffect } from 'react';

type Props = {
    mode: 'create';
    dataProductId: string;
    sourceAligned: boolean;
    identifiers: string[] | undefined;
    external_id: string;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function S3DataOutputForm({ form, external_id, identifiers, sourceAligned }: Props) {
    const { t } = useTranslation();

    const bucketOptions = identifiers?.map((bucket) => ({ label: bucket, value: bucket }));
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
        let prefix = external_id + "/"
        if (sourceAligned) {
            prefix = ""
        }
        if (dataProductNameValue) {
            form.setFieldsValue({ prefix: prefix + generateExternalIdFromName(dataProductNameValue) });
        } else {
            form.setFieldsValue({ prefix: prefix });
        }
    }, [dataProductNameValue, sourceAligned]);

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
            <Form.Item<S3DataOutput & { temp_prefix: string }>
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
                <Input />
            </Form.Item>
            <Form.Item<S3DataOutput>
                required
                hidden={sourceAligned}
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
    );
}