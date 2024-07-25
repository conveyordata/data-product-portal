import { Button, Form, FormProps, Input, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import {
    useGetDataProductByIdQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { DataOutputConfiguration, DataOutputCreate, DataOutputCreateFormSchema, GlueDataOutput, S3DataOutput } from '@/types/data-output';
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
};

export function S3DataOutputForm({ mode, dataProductId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [configurationForm, setConfigurationForm] = useState<Element | null>();
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps<DataPlatforms> | undefined>(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps<DataPlatforms> | undefined>(undefined);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId);
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const [form] = Form.useForm<DataOutputConfiguration>();
    const dataProductNameValue = Form.useWatch('name', form);
    const canFillInForm = mode === 'create';
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const isLoading = isCreating || isCreating || isFetchingInitialValues;
    const onCancel = () => {
        form.resetFields();
    }

    const onSubmitFailed: FormProps<DataOutputConfiguration>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };
    return (
        <div>
            <Form.Item<S3DataOutput>
                        required
                        name={'bucket'}
                        label={t('Bucket')}
                        tooltip={t('The name of the S3 bucket to link the data output to')}
                    >
                        <Input />
                    </Form.Item>
                    <Form.Item<S3DataOutput>
                        required
                        name={'prefix'}
                        label={t('Prefix')}
                        tooltip={t('The name of the prefix to give write access to')}
                    >
                        <Input/>
                    </Form.Item>
                    <Form.Item<S3DataOutput>
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
                    </Form.Item>
        </div>
    )
};
