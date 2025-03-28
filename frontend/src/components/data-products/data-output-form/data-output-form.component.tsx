import { Form, type FormInstance, type FormProps, Input, Select, Space } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { type RefObject, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllPlatformsConfigsQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import type { DataOutputConfiguration, DataOutputCreate, DataOutputCreateFormSchema } from '@/types/data-output';
import { DataOutputStatus } from '@/types/data-output/data-output.contract';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { createDataProductIdPath } from '@/types/navigation.ts';
import type { CustomDropdownItemProps } from '@/types/shared';
import { getDataPlatforms } from '@/utils/data-platforms';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { selectFilterOptionByLabel } from '@/utils/form.helper';

import styles from './data-output-form.module.scss';
import { DatabricksDataOutputForm } from './databricks-data-output-form.component';
import { GlueDataOutputForm } from './glue-data-output-form.component';
import { RedshiftDataOutputForm } from './redshift-data-output-form.component';
import { S3DataOutputForm } from './s3-data-output-form.component';
import { SnowflakeDataOutputForm } from './snowflake-data-output-form.component';

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

    const [identifiers, setIdentifiers] = useState<string[]>([]);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(dataProductId);
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
    const [form] = Form.useForm();
    const sourceAligned = Form.useWatch('is_source_aligned', form);
    const dataProductNameValue = Form.useWatch('name', form);
    const isLoading = isCreating || isCreating || isFetchingInitialValues || isFetchingTags;

    const { data: platformConfig, isLoading: platformsLoading } = useGetAllPlatformsConfigsQuery();

    const dataPlatforms = useMemo(
        () =>
            getDataPlatforms(t).filter((platform) => {
                return (
                    platformConfig?.map((config) => config.service.name).includes(platform.label) ||
                    platformConfig?.map((config) => config.platform.name).includes(platform.label)
                );
            }),
        [t, platformConfig],
    );
    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];

    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (!platformsLoading) {
                const config: DataOutputConfiguration = values as unknown as DataOutputConfiguration;
                switch (selectedConfiguration?.value) {
                    case DataPlatforms.S3: {
                        config['configuration_type'] = 'S3DataOutput';
                        break;
                    }
                    case DataPlatforms.Glue: {
                        config['configuration_type'] = 'GlueDataOutput';
                        break;
                    }
                    case DataPlatforms.Databricks: {
                        config['configuration_type'] = 'DatabricksDataOutput';
                        break;
                    }
                    case DataPlatforms.Snowflake: {
                        config['configuration_type'] = 'SnowflakeDataOutput';
                        break;
                    }
                    case DataPlatforms.Redshift: {
                        config['configuration_type'] = 'RedshiftDataOutput';
                        break;
                    }
                    default: {
                        const errorMessage = 'Data output not configured correctly';
                        dispatchMessage({ content: errorMessage, type: 'error' });
                    }
                }
                const request: DataOutputCreate = {
                    name: values.name,
                    external_id: generateExternalIdFromName(values.name ?? ''),
                    description: values.description,
                    configuration: config,
                    platform_id: platformConfig!.filter(
                        (config) => config.platform.name.toLowerCase() === selectedDataPlatform?.value.toLowerCase(),
                    )[0].platform.id,
                    service_id: platformConfig!.filter(
                        (config) =>
                            config.platform.name.toLowerCase() === selectedDataPlatform?.value.toLowerCase() &&
                            config.service.name.toLowerCase() === selectedConfiguration?.value.toLowerCase(),
                    )[0].service.id,
                    sourceAligned: sourceAligned === undefined ? false : sourceAligned,
                    status: DataOutputStatus.Active,
                    tag_ids: values.tag_ids ?? [],
                };
                await createDataOutput({ id: dataProductId, dataOutput: request }).unwrap();
                dispatchMessage({ content: t('Data output created successfully'), type: 'success' });
                modalCallbackOnSubmit();
                navigate(createDataProductIdPath(dataProductId, TabKeys.DataOutputs));

                form.resetFields();
            }
        } catch (_e) {
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
            setIdentifiers([]);
        } else {
            setSelectedDataPlatform(dropdown);
            if (dropdown!.children?.length === 0) {
                setSelectedConfiguration(dropdown);
                setIdentifiers(
                    platformConfig!.filter(
                        (config) =>
                            config.platform.name.toLowerCase() === dropdown?.value.toLowerCase() &&
                            config.service.name.toLowerCase() === dropdown?.value.toLowerCase(),
                    )[0].config,
                );
            } else {
                setSelectedConfiguration(undefined);
                setIdentifiers([]);
            }
        }
    };

    const onConfigurationClick = (dataPlatform: DataPlatform) => {
        if (!platformsLoading) {
            const dropdown = selectedDataPlatform?.children
                ?.filter((platform) => platform.value === dataPlatform)
                .at(0);
            if (selectedConfiguration !== undefined && selectedConfiguration === dropdown) {
                setSelectedConfiguration(undefined);
                setIdentifiers([]);
            } else {
                setIdentifiers([]);
                setSelectedConfiguration(dropdown);
                setIdentifiers(
                    platformConfig!.filter(
                        (config) =>
                            config.platform.name.toLowerCase() === selectedDataPlatform?.value.toLowerCase() &&
                            config.service.name.toLowerCase() === dropdown?.value.toLowerCase(),
                    )[0].config,
                );
            }
        }
    };

    useEffect(() => {
        if (mode === 'create') {
            form.setFieldsValue({
                external_id: generateExternalIdFromName(dataProductNameValue ?? ''),
                owner: currentDataProduct?.name,
            });
        }
    }, [currentDataProduct?.name, dataProductNameValue, form, mode]);

    const options = [
        { label: t('Product aligned'), value: false },
        { label: t('Source aligned'), value: true },
    ];

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
            disabled={isLoading}
            className={styles.form}
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
            <Form.Item<DataOutputCreateFormSchema> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select data output tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    filterOption={selectFilterOptionByLabel}
                />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema>
                name={'is_source_aligned'}
                valuePropName="checked"
                label={t('Alignment')}
                required
                tooltip={t(
                    'If you follow product thinking approach, select Product aligned. If you want more freedom, you can select Source aligned, however this request will need to be approved by administrators. By default, or when in doubt, leave product aligned selected.',
                )}
            >
                <Select allowClear={false} defaultActiveFirstOption defaultValue={false} options={options} />
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
            <Form.Item hidden={selectedDataPlatform?.children?.length === 0}>
                <Space wrap className={styles.radioButtonContainer}>
                    {selectedDataPlatform?.children
                        ?.filter((platform) => {
                            return platformConfig?.some(
                                (configObj) =>
                                    configObj.platform.name === platform.label ||
                                    configObj.service.name === platform.label,
                            );
                        })
                        .map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={[]}
                                isDisabled={isLoading}
                                isSelected={
                                    selectedConfiguration !== undefined && dataPlatform === selectedConfiguration
                                }
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
                    case DataPlatforms.Redshift:
                        return (
                            <RedshiftDataOutputForm
                                identifiers={identifiers}
                                form={form}
                                external_id={currentDataProduct!.external_id}
                                sourceAligned={sourceAligned}
                            />
                        );
                    case DataPlatforms.Glue:
                        return (
                            <GlueDataOutputForm
                                identifiers={identifiers}
                                form={form}
                                external_id={currentDataProduct!.external_id}
                                sourceAligned={sourceAligned}
                            />
                        ); //mode={mode} dataProductId={dataProductId} />;
                    case DataPlatforms.Databricks:
                        return (
                            <DatabricksDataOutputForm
                                identifiers={identifiers}
                                form={form}
                                external_id={currentDataProduct!.external_id}
                                sourceAligned={sourceAligned}
                            />
                        ); //mode={mode} dataProductId={dataProductId} />;
                    case DataPlatforms.Snowflake:
                        return (
                            <SnowflakeDataOutputForm
                                identifiers={identifiers}
                                form={form}
                                external_id={currentDataProduct!.external_id}
                                sourceAligned={sourceAligned}
                            />
                        );
                    default:
                        return null;
                }
            })()}
        </Form>
    );
}
