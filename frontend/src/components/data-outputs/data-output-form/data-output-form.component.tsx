import { Button, Checkbox, Form, FormInstance, FormProps, Input, Popconfirm, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { DataOutputConfiguration, DataOutputCreate, DataOutputCreateFormSchema } from '@/types/data-output';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { RefObject, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApplicationPaths, createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation.ts';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useCreateDataOutputMutation, useGetDataOutputByIdQuery, useRemoveDataOutputMutation, useUpdateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { CustomDropdownItemProps } from '@/types/shared';
import { S3DataOutputForm } from './s3-data-output-form.component';
import { GlueDataOutputForm } from './glue-data-output-form.component';
import TextArea from 'antd/es/input/TextArea';
import { DataOutputStatus } from '@/types/data-output/data-output.contract';
import { useGetAllPlatformsConfigsQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { getIsDataOutputOwner } from '@/utils/data-output-user-role.helper';
import { getDataProductMemberMemberships, getIsDataProductOwner } from '@/utils/data-product-user-role.helper';
import { current } from '@reduxjs/toolkit';
import { DataOutputUpdateRequest } from '@/types/data-output/data-output-update.contract';
import { ApiUrl, buildUrl } from '@/api/api-urls';

type Props = {
    mode: 'create'|'edit';
    // formRef: RefObject<FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>>;
    dataOutputId: string
    // dataProductId: string;
    // modalCallbackOnSubmit: () => void;
};

export function DataOutputForm({ mode, dataOutputId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<
        CustomDropdownItemProps<DataPlatforms> | undefined
    >(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<
        CustomDropdownItemProps<DataPlatforms> | undefined
    >(undefined);
    const { data: currentDataOutput, isFetching: isFetchingInitialValues } = useGetDataOutputByIdQuery(
        dataOutputId || '',
        {
            skip: mode === 'create' || !dataOutputId,
        },
    );
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(currentDataOutput?.owner.id!, {skip: isFetchingInitialValues || !dataOutputId || mode === 'create' });
    const currentUser = useSelector(selectCurrentUser);
    const [identifiers, setIdentifiers] = useState<string[]>([]);
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const [updateDataOutput, { isLoading: isUpdating }] = useUpdateDataOutputMutation();
    const [archiveDataOutput, { isLoading: isArchiving }] = useRemoveDataOutputMutation();
    const [form] = Form.useForm<DataOutputCreateFormSchema & DataOutputConfiguration>();
    const sourceAligned = Form.useWatch('is_source_aligned', form);
    const dataProductNameValue = Form.useWatch('name', form);
    const canEditForm = Boolean(
        mode === 'edit' &&
            dataProduct &&
            currentUser?.id &&
            (getIsDataProductOwner(dataProduct, currentUser?.id) || currentUser?.is_admin),
    );
    const canFillInForm = mode === 'create' || canEditForm;
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const isLoading = isCreating || isCreating || isFetchingInitialValues;

    // const { data: platformConfig, isFetching: isLoadingPlatformConfigs } = useGetAllPlatformsConfigsQuery()

    const handleArchiveDataProduct = async () => {
        if (canEditForm && currentDataOutput) {
            try {
                await archiveDataOutput(currentDataOutput?.id).unwrap();
                dispatchMessage({ content: t('Data output archived successfully'), type: 'success' });
                navigate(ApplicationPaths.DataOutputs);
            } catch (error) {
                dispatchMessage({
                    content: t('Failed to archive data output, please try again later'),
                    type: 'error',
                });
            }
        }
    };
    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            // if (mode === 'create') {
            //     // TODO This is ugly code. We pass along the entire form in the configuration currently.
            //     // Should be rewritten to only pass the config attributes
            //     const config: DataOutputConfiguration = values as unknown as DataOutputConfiguration;
            //     const request: DataOutputCreate = {
            //         name: values.name,
            //         external_id: generateExternalIdFromName(values.name ?? ''),
            //         description: values.description,
            //         configuration: config,
            //         platform_id: platformConfig?.filter((config) => config.platform.name.toLowerCase() === selectedDataPlatform?.value.toLowerCase())[0].platform.id!,
            //         service_id: platformConfig?.filter((config) => config.platform.name.toLowerCase() === selectedDataPlatform?.value.toLowerCase() && config.service.name.toLowerCase() === selectedConfiguration?.value.toLowerCase())[0].service.id!,
            //         owner_id: dataProductId,
            //         sourceAligned: sourceAligned === undefined ? false : sourceAligned,
            //         status: DataOutputStatus.Active
            //     };
            //     await createDataOutput(request).unwrap();
            //     dispatchMessage({ content: t('Data output created successfully'), type: 'success' });
            //     modalCallbackOnSubmit();
            //     navigate(createDataProductIdPath(dataProductId));
            // }

            if (mode === 'edit' && dataOutputId) {
                if (!canEditForm) {
                    dispatchMessage({ content: t('You are not allowed to edit this data output'), type: 'error' });
                    return;
                };

                // TODO Figure out what fields are updateable and which are not
                const request: DataOutputUpdateRequest = {
                    name: values.name,
                    // external_id: values.external_id,
                    description: values.description,
                    // owner_id: values.owner_id,
                    // platform_id: values.platform_id,
                    // service_id: values.service_id,
                    // status: values.status,
                    // configuration: values.configuration,
                    // sourceAligned: values.sourceAligned
                };
                console.log(buildUrl(ApiUrl.DataOutputGet, { dataOutputId: dataOutputId }),)
                const response = await updateDataOutput({
                    dataOutput: request,
                    dataOutputId: dataOutputId,
                }).unwrap();
                dispatchMessage({ content: t('Data output updated successfully'), type: 'success' });

                navigate(createDataOutputIdPath(response.id));
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

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && dataOutputId) {
            navigate(createDataOutputIdPath(dataOutputId));
        } else {
            navigate(ApplicationPaths.DataOutputs);
        }
    };

    useEffect(() => {
        if (currentDataOutput && mode === 'edit') {
            form.setFieldsValue({
                owner_id: currentDataOutput.owner_id,
                name: currentDataOutput.name,
                description: currentDataOutput.description,
                // type_id: currentDataProduct.type.id,
                // business_area_id: currentDataProduct.business_area.id,
                // tags: currentDataProduct.tags.map((tag) => tag.value),
                // owners: getDataProductOwnerIds(currentDataProduct),
            });
        }
    }, [currentDataOutput, mode]);

    // useEffect(() => {
    //     if (mode === 'create') {
    //         form.setFieldsValue({
    //             external_id: generateExternalIdFromName(dataProductNameValue ?? ''),
    //             owner: currentDataOutput?.name,
    //         });
    //     }
    // }, [dataProductNameValue]);

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
            {/* <Form.Item<DataOutputCreateFormSchema>
                name={'is_source_aligned'} valuePropName="checked"
            >
                <Checkbox>{t('Is source aligned')}</Checkbox>
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
                                identifiers={identifiers}
                                sourceAligned={sourceAligned}
                                external_id={currentDataProduct!.external_id}
                                mode={mode}
                                dataProductId={dataProductId}
                            />
                        );
                    case DataPlatforms.Glue:
                        return <GlueDataOutputForm identifiers={identifiers} form={form} external_id={currentDataProduct!.external_id} sourceAligned={sourceAligned}/>; //mode={mode} dataProductId={dataProductId} />;
                    default:
                        return null;
                }
            })()} */}
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreating || isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {mode === 'edit' ? t('Edit') : t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isCreating || isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Cancel')}
                    </Button>
                    {canEditForm && (
                        <Popconfirm
                            title={t('Are you sure you want to archive this data output?')}
                            onConfirm={handleArchiveDataProduct}
                            okText={t('Yes')}
                            cancelText={t('No')}
                        >
                            <Button
                                className={styles.formButton}
                                type="default"
                                danger
                                loading={isArchiving}
                                disabled={isLoading}
                            >
                                {t('Archive')}
                            </Button>
                        </Popconfirm>
                    )}
                </Space>
            </Form.Item>
        </Form>
    );
}
