import { FormInstance, Input, Select } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputCreateFormSchema } from '@/types/data-output';
import { DataPlatforms } from '@/types/data-platform';

import { configurationFieldName } from './components/configuration-field-name';
import { ConfigurationFormItem } from './components/output-configuration-form-item';
import { ConfigurationSubForm } from './components/output-configuration-sub-form.component';

type Props = {
    form: FormInstance<DataOutputCreateFormSchema>;
    namespace: string;
    identifiers?: string[];
    sourceAligned: boolean;
};

export function S3DataOutputForm({ form, namespace, identifiers = [], sourceAligned }: Props) {
    const { t } = useTranslation();

    const bucketOptions = identifiers.map((bucket) => ({ label: bucket, value: bucket }));

    useEffect(() => {
        form.setFieldValue(configurationFieldName('suffix'), sourceAligned ? '' : namespace);
    }, [form, sourceAligned, namespace]);

    return (
        <ConfigurationSubForm
            form={form}
            platform={DataPlatforms.S3}
            resultLabel={t('Resulting path')}
            resultTooltip={t('The path on S3 you can access through this data output')}
        >
            <ConfigurationFormItem
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
            </ConfigurationFormItem>
            <ConfigurationFormItem name={'suffix'} hidden>
                <Input />
            </ConfigurationFormItem>
            <ConfigurationFormItem
                name={'path'}
                label={t('Path')}
                tooltip={t('The name of the path to give write access to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the path of this data output'),
                    },
                    {
                        pattern: /^[a-zA-Z0-9._/-]+$/,
                        message: t('The path can only contain letters, numbers, dots, underscores, dashes and slashes'),
                    },
                ]}
            >
                <Input />
            </ConfigurationFormItem>
        </ConfigurationSubForm>
    );
}
