import { Button, Form, FormProps, Input, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import {
    useGetDataProductByIdQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { DataOutputConfiguration, DataOutputCreate, DataOutputCreateFormSchema } from '@/types/data-output';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { CustomDropdownItemProps } from '@/types/shared';
import { S3DataOutputForm } from './s3-data-output-form.component';
import { GlueDataOutputForm } from './glue-data-output-form.component';

type Props = {
    mode: 'create';
    dataProductId: string;
};

export function DataOutputForm({ mode, dataProductId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps<DataPlatforms> | undefined>(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps<DataPlatforms> | undefined>(undefined);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId);
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const [form] = Form.useForm<DataOutputCreateFormSchema>();
    const dataProductNameValue = Form.useWatch('name', form);
    const canFillInForm = mode === 'create';
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const isLoading = isCreating || isCreating || isFetchingInitialValues;

    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (mode === 'create') {
                // TODO This is ugly code. We pass along the entire form in the configuration currently.
                // Should be rewritten to only pass the config attributes
                const config: DataOutputConfiguration = values as unknown as DataOutputConfiguration;

                const request: DataOutputCreate = {
                    name: values.name,
                    external_id: values.external_id,
                    configuration: config,
                    owner_id: dataProductId,
                };
                const response = await createDataOutput(request).unwrap();
                dispatchMessage({ content: t('Data product created successfully'), type: 'success' });
                navigate(createDataProductIdPath(dataProductId));
            }

            form.resetFields();
        } catch (e) {
            const errorMessage = ('Failed to create data output');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataOutputCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onDataPlatformClick = (dataPlatform: DataPlatform) => {
        const dropdown = dataPlatforms.filter((platform) => (platform.value === dataPlatform)).at(0)
        if (selectedDataPlatform !== undefined && selectedDataPlatform === dropdown) {
            setSelectedDataPlatform(undefined)
            setSelectedConfiguration(undefined)
        } else {
            setSelectedDataPlatform(dropdown)
        }
    }

    const onConfigurationClick = (dataPlatform: DataPlatform) => {
        const dropdown = selectedDataPlatform?.children?.filter((platform) => (platform.value === dataPlatform)).at(0)
        if (selectedConfiguration !== undefined && selectedConfiguration === dropdown) {
            setSelectedConfiguration(undefined)
        } else {
            setSelectedConfiguration(dropdown)
        }
    }

    const onCancel = () => {
        form.resetFields();
    }
    useEffect(() => {
        if (mode === 'create') {
            form.setFieldsValue({ external_id: generateExternalIdFromName(dataProductNameValue ?? ''), owner: currentDataProduct?.name });
        }
    }, [dataProductNameValue]);
// TODO Solve error with form can not be descendant of form!
    return (
        <Form
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onSubmit}
            onFinishFailed={onSubmitFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            labelWrap
            disabled={isLoading || !canFillInForm}
        >
            <Form.Item<DataOutputCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your data output')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the data output'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            {/*Disabled field that will render an external ID everytime the name changes*/}
            <Form.Item<DataOutputCreateFormSchema>
                required
                name={'external_id'}
                label={t('External ID')}
                tooltip={t('The external ID of the data product')}
            >
                <Input disabled />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema>
                required
                name={'owner'}
                label={t('Owner')}
                tooltip={t('The data product that owns the data output')}
            >
                <Input disabled />
            </Form.Item>
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                        {dataPlatforms.filter((dataPlatform) => (dataPlatform.hasConfig)).map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={[]}
                                isDisabled={isLoading}
                                isLoading={isLoading}
                                isSelected={selectedDataPlatform !== undefined && dataPlatform === selectedDataPlatform }
                                //onMenuItemClick={onDataPlatformClick}
                                onTileClick={onDataPlatformClick}
                            />
                        ))}
                    </Space>
            </Form.Item>
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                    {/* TODO Fetch correct data platform children */}
                        {selectedDataPlatform?.children?.map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={[]}
                                isDisabled={isLoading}
                                isSelected={selectedConfiguration !== undefined && dataPlatform === selectedConfiguration}
                                isLoading={isLoading}
                                //isDisabled={isDisabled || isLoading || isLoadingEnvironments || !canAccessData}
                                //isLoading={isLoading || isLoadingEnvironments}
                                //onMenuItemClick={onDataPlatformClick}
                                onTileClick={onConfigurationClick}
                            />
                        ))}
                    </Space>
            </Form.Item>
            {(() => {
                switch (selectedConfiguration?.value) {
                case DataPlatforms.S3:
                    return <S3DataOutputForm mode={mode} dataProductId={dataProductId}/>
                case DataPlatforms.Glue:
                    return <GlueDataOutputForm mode={mode} dataProductId={dataProductId}/>
                default:
                    return null
                }
            })()}
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isCreating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Cancel')}
                    </Button>
                </Space>
            </Form.Item>
        </Form>
    );
}
