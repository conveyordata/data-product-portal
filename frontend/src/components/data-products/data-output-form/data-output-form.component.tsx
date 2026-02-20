import { Form, type FormInstance, type FormProps, Input, Radio, Select, Space } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { type RefObject, useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';

import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { useGetAllPlatformServiceConfigurationsQuery } from '@/store/api/services/generated/configurationPlatformsApi.ts';
import { useGetTagsQuery } from '@/store/api/services/generated/configurationTagsApi.ts';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    type CreateTechnicalAssetRequest,
    useCreateTechnicalAssetMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import {
    type PlatformTile,
    useGetPlatformTilesQuery,
    useGetPluginsQuery,
    useRenderTechnicalAssetAccessPathMutation,
} from '@/store/api/services/generated/pluginsApi';
import {
    ResourceNameModel,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
    useResourceNameConstraintsQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { type DataOutputCreateFormSchema, DataOutputStatus } from '@/types/data-output';
import { createDataProductIdPath } from '@/types/navigation';
import type { CustomDropdownItemProps } from '@/types/shared';
import { selectFilterOptionByLabel } from '@/utils/form.helper';
import { getIcon } from '@/utils/icon-loader';
import { DataOutputConfigurationForm } from './data-output-configuration-form.component';
import styles from './data-output-form.module.scss';

type Props = {
    mode: 'create';
    formRef: RefObject<FormInstance<CreateTechnicalAssetRequest> | null>;
    dataProductId: string;
    modalCallbackOnSubmit: () => void;
};

type ServiceConfig = {
    platform_id: string;
    service_id: string;
    configuration: string[];
};

const DEBOUNCE = 500;

export function DataOutputForm({ mode, formRef, dataProductId, modalCallbackOnSubmit }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();

    // Data
    const { data: { plugins: uiMetadataGroups } = {}, isLoading: isLoadingMetadata } = useGetPluginsQuery();
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductQuery(dataProductId);
    const { data: { tags: availableTags = [] } = {}, isFetching: isFetchingTags } = useGetTagsQuery();
    const { data: { platform_service_configurations: platformConfig = [] } = {}, isLoading: platformsLoading } =
        useGetAllPlatformServiceConfigurationsQuery();

    const [createTechnicalAsset, { isLoading: isCreating }] = useCreateTechnicalAssetMutation();

    // State
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps<string> | undefined>(
        undefined,
    );
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps<string> | undefined>(
        undefined,
    );

    // Form
    const [form] = Form.useForm();
    const technical_mapping = Form.useWatch('technical_mapping', form);
    const dataOutputNameValue = Form.useWatch('name', form);

    // Namespace validation
    const [sanitizeResourceName, { data: sanitizedResourceName }] = useLazySanitizeResourceNameQuery();
    const [validateNamespace] = useLazyValidateResourceNameQuery();
    const { data: constraints } = useResourceNameConstraintsQuery();
    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);

    // Result string
    const [fetchResultString] = useRenderTechnicalAssetAccessPathMutation();

    const isLoading = platformsLoading || isLoadingMetadata || isCreating || isFetchingInitialValues || isFetchingTags;

    const tagSelectOptions = availableTags.map((tag) => ({ label: tag.value, value: tag.id }));

    // Get platform tiles from backend
    const { data: { platform_tiles: platformTilesDataUnfiltered } = {} } = useGetPlatformTilesQuery();
    const platformTilesData = useMemo(() => {
        if (!platformTilesDataUnfiltered) {
            return [];
        }
        // Filter out platforms that are not meant to be shown in the form
        return platformTilesDataUnfiltered.filter((tile) => tile.show_in_form);
    }, [platformTilesDataUnfiltered]);
    // Transform backend tiles to frontend format with icon components
    const dataPlatforms = useMemo(() => {
        if (!platformTilesData) {
            return [];
        }

        const transformTile = (tile: PlatformTile): CustomDropdownItemProps<string> => ({
            label: t(tile.label),
            value: tile.value,
            icon: getIcon(tile.icon_name),
            hasEnvironments: tile.has_environments,
            hasConfig: tile.has_config,
            children: tile.children?.map(transformTile) || [],
        });

        return platformTilesData.map(transformTile);
    }, [platformTilesData, t]);

    const platformServiceConfigMap = useMemo(() => {
        const map = new Map<string, ServiceConfig>();

        if (!platformConfig) {
            return map;
        }
        for (const config of platformConfig) {
            const platform = (
                config.platform.name === config.service.name ? config.platform.name : config.service.name
            ).toLocaleLowerCase();

            map.set(platform, {
                platform_id: config.platform.id,
                service_id: config.service.id,
                configuration: config.config,
            });
        }

        return map;
    }, [platformConfig]);

    const onSubmit: FormProps<CreateTechnicalAssetRequest>['onFinish'] = async (values) => {
        try {
            if (!platformsLoading) {
                await createTechnicalAsset({ dataProductId, createTechnicalAssetRequest: values }).unwrap();
                dispatchMessage({ content: t('Technical Asset created successfully'), type: 'success' });
                modalCallbackOnSubmit();
                navigate(createDataProductIdPath(dataProductId, TabKeys.OutputPorts));

                form.resetFields();
            }
        } catch (_e) {
            const errorMessage = 'Failed to create Technical Asset';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<CreateTechnicalAssetRequest>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onDataPlatformClick = (dropdown: CustomDropdownItemProps<string>) => {
        if (selectedDataPlatform !== dropdown) {
            form.setFieldsValue({ configuration: undefined, result: undefined });
            setSelectedDataPlatform(dropdown);

            if (dropdown.children?.length === 0) {
                setSelectedConfiguration(dropdown);
                form.setFieldValue('service_id', platformServiceConfigMap.get(dropdown.value)?.service_id);
            } else {
                setSelectedConfiguration(undefined);
            }
        }
    };

    const onConfigurationClick = (dropdown: CustomDropdownItemProps<string>) => {
        if (!platformsLoading) {
            if (selectedConfiguration !== dropdown) {
                form.setFieldsValue({ configuration: undefined, result: undefined });
                setSelectedConfiguration(dropdown);
            }
        }
    };

    // Namespace validation
    const fetchNamespaceDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), DEBOUNCE);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFields([
                {
                    name: 'namespace',
                    validating: true,
                    errors: [],
                },
            ]);
            fetchNamespaceDebounced(dataOutputNameValue ?? '');
        }
    }, [mode, form, canEditNamespace, dataOutputNameValue, fetchNamespaceDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditNamespace) {
            form.setFieldValue('namespace', sanitizedResourceName?.resource_name);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditNamespace, sanitizedResourceName]);

    const options = [
        { label: t('Default'), value: 'default' },
        { label: t('Custom'), value: 'custom' },
    ];

    const validateNamespaceCallback = useCallback(
        (namespace: string) =>
            validateNamespace({
                dataProductId: dataProductId,
                resourceName: namespace,
                model: ResourceNameModel.OutputPort,
            }).unwrap(),
        [validateNamespace, dataProductId],
    );

    // Result string
    const setResultString = useDebouncedCallback((values: CreateTechnicalAssetRequest) => {
        form.validateFields(['configuration'], { validateOnly: true, recursive: true })
            .then(() => {
                const request = {
                    platform_id: values.platform_id,
                    service_id: values.service_id,
                    configuration: values.configuration,
                };
                return fetchResultString(request).unwrap();
            })
            .then((result) => form.setFieldValue('result', result.technical_asset_access_path))
            .catch(() => form.setFieldValue('result', undefined));
    }, DEBOUNCE);

    const onValuesChange: FormProps<CreateTechnicalAssetRequest>['onValuesChange'] = (
        changed,
        values: CreateTechnicalAssetRequest,
    ) => {
        if (changed.configuration) {
            setResultString(values);
        }
    };

    return (
        <Form
            form={form}
            ref={formRef}
            layout="vertical"
            onFinish={onSubmit}
            onFinishFailed={onSubmitFailed}
            onValuesChange={onValuesChange}
            autoComplete={'off'}
            requiredMark={'optional'}
            labelWrap
            disabled={isLoading}
        >
            <Form.Item<DataOutputCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Technical Asset')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Technical Asset'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <ResourceNameFormItem
                form={form}
                tooltip={t('The namespace of the Technical Asset')}
                max_length={constraints?.max_length}
                canEditResourceName={canEditNamespace}
                toggleCanEditResourceName={() => setCanEditNamespace((prev) => !prev)}
                validationRequired
                validateResourceName={validateNamespaceCallback}
            />
            <Form.Item<DataOutputCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the Technical Asset')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Technical Asset'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than 255 characters'),
                    },
                ]}
            >
                <TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema> name={'tag_ids'} label={t('Tags')} initialValue={[]}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select Technical Asset tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabel }}
                />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema>
                name={'status'}
                required
                hidden
                initialValue={DataOutputStatus.Active}
            />
            <Form.Item<DataOutputCreateFormSchema>
                name={'technical_mapping'}
                label={t('Technical Mapping')}
                required
                tooltip={t(
                    'Default mapping applies the platform’s standards to your asset. Choose Custom if your asset exists outside these standards and requires explicit configuration, which may be subject to manual approval before activation.',
                )}
                initialValue={'default'}
            >
                <Select allowClear={false} options={options} />
            </Form.Item>
            <Form.Item name={'platform_id'}>
                <Radio.Group>
                    <Space wrap className={styles.radioButtonContainer}>
                        {dataPlatforms.map((dataPlatform) => (
                            <DataOutputPlatformTile<string>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                isDisabled={isLoading}
                                isLoading={isLoading}
                                isSelected={dataPlatform === selectedDataPlatform}
                                onTileClick={onDataPlatformClick}
                                value={
                                    platformConfig?.find((config) => config.platform.name === dataPlatform.label)
                                        ?.platform.id
                                }
                            />
                        ))}
                    </Space>
                </Radio.Group>
            </Form.Item>
            <Form.Item name={'service_id'} hidden={selectedDataPlatform?.children?.length === 0}>
                <Radio.Group>
                    <Space wrap className={styles.radioButtonContainer}>
                        {selectedDataPlatform?.children?.map((dataPlatform) => (
                            <DataOutputPlatformTile<string>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                isDisabled={isLoading}
                                isSelected={dataPlatform === selectedConfiguration}
                                isLoading={isLoading}
                                onTileClick={onConfigurationClick}
                                value={platformServiceConfigMap.get(dataPlatform.value)?.service_id}
                            />
                        ))}
                    </Space>
                </Radio.Group>
            </Form.Item>
            {(() => {
                if (!currentDataProduct || !selectedConfiguration || !uiMetadataGroups) {
                    return null;
                }

                // Find the metadata for the selected platform
                const pluginMetadata = uiMetadataGroups.find(
                    (meta) => meta.platform === selectedConfiguration.value.toLowerCase(),
                );

                if (!pluginMetadata) {
                    return null;
                }

                return (
                    <DataOutputConfigurationForm
                        form={form}
                        uiMetadataGroups={pluginMetadata.ui_metadata}
                        namespace={currentDataProduct.namespace}
                        technical_mapping={technical_mapping}
                        configurationType={pluginMetadata.plugin}
                        resultLabel={pluginMetadata.result_label ?? ''}
                        resultTooltip={pluginMetadata.result_tooltip ?? ''}
                    />
                );
            })()}
        </Form>
    );
}
