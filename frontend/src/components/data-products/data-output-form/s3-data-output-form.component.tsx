import { Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputConfiguration, DataOutputCreateFormSchema, S3DataOutput } from '@/types/data-output';
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
    const dataProductNameValue: string = Form.useWatch('temp_path', form);
    const bucketValue: string = Form.useWatch('bucket', form);
    useEffect(() => {
        let path = external_id + '/';
        if (sourceAligned) {
            path = '';
        }
        if (dataProductNameValue) {
            form.setFieldsValue({ path: path + generateExternalIdFromName(dataProductNameValue) });
            form.setFieldsValue({
                result: bucketValue + '/' + path + generateExternalIdFromName(dataProductNameValue),
            });
        } else {
            form.setFieldsValue({ path: path });
            form.setFieldsValue({ result: bucketValue + '/' + path });
        }
    }, [dataProductNameValue, sourceAligned, bucketValue, external_id, form]);

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
                <Select allowClear showSearch options={bucketOptions} />
            </Form.Item>
            <Form.Item<S3DataOutput & { temp_path: string }>
                name={'temp_path'}
                label={t('Path')}
                tooltip={t('The name of the path to give write access to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the path of this data output'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<S3DataOutput> required hidden={true} name={'path'}>
                <Input disabled />
            </Form.Item>
            <Form.Item<S3DataOutput & { result: string }>
                required
                name={'result'}
                label={t('Resulting path')}
                tooltip={t('The path on s3 you can access through this data output')}
            >
                <Input disabled />
            </Form.Item>
        </div>
    );
}
