import { Form, FormInstance, FormProps, Input, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { DataOutputConfiguration, DataOutputCreate, DataOutputCreateFormSchema } from '@/types/data-output';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { RefObject, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { CustomDropdownItemProps } from '@/types/shared';
import { S3DataOutputForm } from './s3-data-output-form.component';
import { GlueDataOutputForm } from './glue-data-output-form.component';
import TextArea from 'antd/es/input/TextArea';
import { DataOutputStatus } from '@/types/data-output/data-output.contract';

type Props = {
    mode: 'create';
    formRef: RefObject<FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>>;
    dataProductId: string;
    modalCallbackOnSubmit: () => void;
};

export function DataOutputForm({ mode, formRef, dataProductId, modalCallbackOnSubmit }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<
        CustomDropdownItemProps<DataPlatforms> | undefined
    >(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<
        CustomDropdownItemProps<DataPlatforms> | undefined
    >(undefined);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(dataProductId);
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const [form] = Form.useForm<DataOutputCreateFormSchema & DataOutputConfiguration>();
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
                    external_id: generateExternalIdFromName(values.name ?? ''),
                    description: values.description,
                    configuration: config,
                    owner_id: dataProductId,
                    status: DataOutputStatus.Active
                };
                await createDataOutput(request).unwrap();
                dispatchMessage({ content: t('Data output created successfully'), type: 'success' });
                modalCallbackOnSubmit();
                navigate(createDataProductIdPath(dataProductId));
            }

            form.resetFields();
        } catch (e) {
            const errorMessage = 'Failed to create data output';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataOutputCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onDataPlatformClick = (dataPlatform: DataPlatform) => {
        const dropdown = dataPlatforms.filter((platform) => platform.value === dataPlatform).at(0);
        if (selectedDataPlatform !== undefined && selectedDataPlatform === dropdown) {
            setSelectedDataPlatform(undefined);
            setSelectedConfiguration(undefined);
        } else {
            setSelectedDataPlatform(dropdown);
        }
    };

    const onConfigurationClick = (dataPlatform: DataPlatform) => {
        const dropdown = selectedDataPlatform?.children?.filter((platform) => platform.value === dataPlatform).at(0);
        if (selectedConfiguration !== undefined && selectedConfiguration === dropdown) {
            setSelectedConfiguration(undefined);
        } else {
            setSelectedConfiguration(dropdown);
        }
    };

    useEffect(() => {
        if (mode === 'create') {
            form.setFieldsValue({
                external_id: generateExternalIdFromName(dataProductNameValue ?? ''),
                owner: currentDataProduct?.name,
            });
        }
    }, [dataProductNameValue]);
    // TODO Required fields of nested elements do not transcent
    return (
        <Form
            form={form}
            ref={formRef}
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
            <Form.Item<DataOutputCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the data output')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the data output'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than 255 characters'),
                    },
                ]}
            >
                <TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                    {dataPlatforms
                        .filter((dataPlatform) => dataPlatform.hasConfig)
                        .map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={[]}
                                isDisabled={isLoading}
                                isLoading={isLoading}
                                isSelected={selectedDataPlatform !== undefined && dataPlatform === selectedDataPlatform}
                                onTileClick={onDataPlatformClick}
                            />
                        ))}
                </Space>
            </Form.Item>
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                    {selectedDataPlatform?.children?.map((dataPlatform) => (
                        <DataOutputPlatformTile<DataPlatform>
                            key={dataPlatform.value}
                            dataPlatform={dataPlatform}
                            environments={[]}
                            isDisabled={isLoading}
                            isSelected={selectedConfiguration !== undefined && dataPlatform === selectedConfiguration}
                            isLoading={isLoading}
                            onTileClick={onConfigurationClick}
                        />
                    ))}
                </Space>
            </Form.Item>
            {(() => {
                switch (selectedConfiguration?.value) {
                    case DataPlatforms.S3:
                        return (
                            <S3DataOutputForm
                                form={form}
                                external_id={currentDataProduct?.external_id}
                                mode={mode}
                                dataProductId={dataProductId}
                            />
                        );
                    case DataPlatforms.Glue:
                        return <GlueDataOutputForm />; //mode={mode} dataProductId={dataProductId} />;
                    default:
                        return null;
                }
            })()}
        </Form>
    );
}