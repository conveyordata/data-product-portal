import { Form, type FormInstance, type FormProps, Input, Radio, Select, Space } from 'antd';
import { type RefObject, useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDebouncedCallback } from 'use-debounce';
import { CardSelection } from '@/components/card-selection/card-selection.tsx';
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import { TechnicalAssetPlatformTile } from '@/components/technical-assets/technical-asset-platform-tile/technical-asset-platform-tile.component';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { useGetAccessModesQuery } from '@/store/api/services/generated/configurationAccessModesApi.ts';
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
import type { CustomDropdownItemProps } from '@/types/shared';
import type { TechnicalAssetsCreateForm } from '@/types/technical-asset';
import { dispatchMessage } from '@/utils/feedback.ts';
import { selectFilterOptionByLabel } from '@/utils/form.helper';
import { getIcon } from '@/utils/icon-loader';
import { AccessModeSelector } from './access-mode-selector.component';
import { TechnicalAssetConfigurationForm } from './technical-asset-configuration-form.component';
import styles from './technical-asset-form.module.scss';

const { TextArea } = Input;

type Props = {
    mode: 'create';
    formRef: RefObject<FormInstance<CreateTechnicalAssetRequest> | null>;
    dataProductId: string;
    modalCallbackOnSubmit: () => void;
    debounce?: number;
};

type ServiceConfig = {
    platform_id: string;
    service_id: string;
    configuration: string[];
};

type AccessModeType = 'single' | 'multiple';

export function TechnicalAssetForm({ mode, formRef, dataProductId, modalCallbackOnSubmit, debounce = 500 }: Props) {
    const { t } = useTranslation();

    const { data: { plugins: uiMetadataGroups } = {}, isLoading: isLoadingMetadata } = useGetPluginsQuery();
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductQuery(dataProductId);
    const { data: { tags: availableTags = [] } = {}, isFetching: isFetchingTags } = useGetTagsQuery();
    const { data: { access_modes: accessModes = [] } = {}, isFetching: isFetchingAccessModes } =
        useGetAccessModesQuery();
    const { data: { platform_service_configurations: platformConfig = [] } = {}, isLoading: platformsLoading } =
        useGetAllPlatformServiceConfigurationsQuery();

    const [createTechnicalAsset, { isLoading: isCreating }] = useCreateTechnicalAssetMutation();

    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps<string> | undefined>(
        undefined,
    );
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps<string> | undefined>(
        undefined,
    );

    const [form] = Form.useForm();
    const technical_mapping = Form.useWatch('technical_mapping', form);
    const dataOutputNameValue = Form.useWatch('name', form);

    const [sanitizeResourceName, { data: sanitizedResourceName }] = useLazySanitizeResourceNameQuery();
    const [validateNamespace] = useLazyValidateResourceNameQuery();
    const { data: constraints } = useResourceNameConstraintsQuery();
    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);
    const accessMode = Form.useWatch('access_mode_type', form) as 'single' | 'multiple' | undefined;

    const [fetchResultString] = useRenderTechnicalAssetAccessPathMutation();

    const isLoading =
        platformsLoading ||
        isLoadingMetadata ||
        isCreating ||
        isFetchingInitialValues ||
        isFetchingTags ||
        isFetchingAccessModes;

    const tagSelectOptions = availableTags.map((tag) => ({ label: tag.value, value: tag.id }));
    const { data: { platform_tiles: platformTilesDataUnfiltered } = {} } = useGetPlatformTilesQuery();
    const platformTilesData = useMemo(() => {
        if (!platformTilesDataUnfiltered) {
            return [];
        }
        return platformTilesDataUnfiltered.filter((tile) => tile.show_in_form);
    }, [platformTilesDataUnfiltered]);
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
            await createTechnicalAsset({ dataProductId, createTechnicalAssetRequest: values }).unwrap();
            dispatchMessage({ content: t('Technical Asset created successfully'), type: 'success' });
            modalCallbackOnSubmit();
            form.resetFields();
        } catch (_e) {
            const errorMessage = 'Failed to create Technical Asset';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
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
    const fetchNamespaceDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), debounce);

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
    }, debounce);

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
            onValuesChange={onValuesChange}
            autoComplete="off"
            labelWrap
            disabled={isLoading}
        >
            <Form.Item<TechnicalAssetsCreateForm>
                name="name"
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
            <Form.Item<TechnicalAssetsCreateForm>
                name="description"
                label={t('Description')}
                tooltip={t('A description for your Technical Asset')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Technical Asset'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than {{length}} characters', {
                            length: MAX_DESCRIPTION_INPUT_LENGTH,
                        }),
                    },
                ]}
            >
                <TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item<TechnicalAssetsCreateForm> name="tag_ids" label={t('Tags')} initialValue={[]}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select Technical Asset tags')}
                    mode="multiple"
                    options={tagSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabel }}
                />
            </Form.Item>
            <Form.Item<TechnicalAssetsCreateForm>
                name="technical_mapping"
                label={t('Technical Mapping')}
                required
                tooltip={t(
                    'Default mapping applies the platform’s standards to your asset. Choose Custom if your asset exists outside these standards and requires explicit configuration, which may be subject to manual approval before activation.',
                )}
                initialValue="default"
            >
                <Select allowClear={false} options={options} />
            </Form.Item>

            <Form.Item name="platform_id">
                <Radio.Group>
                    <Space wrap className={styles.radioButtonContainer}>
                        {dataPlatforms.map((dataPlatform) => (
                            <TechnicalAssetPlatformTile<string>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                isDisabled={isLoading}
                                isSelected={dataPlatform === selectedDataPlatform}
                                onTileClick={onDataPlatformClick}
                                value={
                                    platformConfig?.find(
                                        (config) =>
                                            config.platform.name.toLowerCase() === dataPlatform.label.toLowerCase(),
                                    )?.platform.id
                                }
                            />
                        ))}
                    </Space>
                </Radio.Group>
            </Form.Item>
            <Form.Item name="service_id" hidden={selectedDataPlatform?.children?.length === 0}>
                <Radio.Group>
                    <Space wrap className={styles.radioButtonContainer}>
                        {selectedDataPlatform?.children?.map((dataPlatform) => (
                            <TechnicalAssetPlatformTile<string>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                isDisabled={isLoading}
                                isSelected={dataPlatform === selectedConfiguration}
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
                    <>
                        <TechnicalAssetConfigurationForm
                            form={form}
                            uiMetadataGroups={pluginMetadata.ui_metadata}
                            namespace={currentDataProduct.namespace}
                            technical_mapping={technical_mapping}
                            configurationType={pluginMetadata.plugin}
                            resultLabel={pluginMetadata.result_label ?? ''}
                            resultTooltip={pluginMetadata.result_tooltip ?? ''}
                        />

                        <Form.Item<TechnicalAssetsCreateForm>
                            name="access_mode_type"
                            label={t('Access mode')}
                            rules={[{ required: true, message: t('Please select an access mode') }]}
                        >
                            <CardSelection<AccessModeType>
                                style={{ padding: '4px' }}
                                options={[
                                    {
                                        value: 'single',
                                        title: t('Single access mode'),
                                        description: t(
                                            'Assign one access level to all users who connect to this asset.',
                                        ),
                                    },
                                    {
                                        value: 'multiple',
                                        title: t('Configure access modes'),
                                        description: t(
                                            "Define multiple access modes for this asset. You'll be able to create custom access levels with specific permissions, connection strings, and configurations.",
                                        ),
                                    },
                                ]}
                            />
                        </Form.Item>

                        <Form.Item
                            name="access_mode_ids"
                            label={t('Access modes')}
                            initialValue={[]}
                            hidden={accessMode !== 'multiple'}
                            dependencies={['access_mode_type']}
                            rules={[
                                {
                                    validator: async (_, value) => {
                                        if (accessMode === 'multiple' && (!value || value.length === 0)) {
                                            return Promise.reject(
                                                new Error(t('Please select at least one access mode')),
                                            );
                                        }
                                    },
                                },
                            ]}
                        >
                            <AccessModeSelector
                                accessModes={accessModes}
                                loading={isFetchingAccessModes}
                                selectionMode="multiple"
                            />
                        </Form.Item>
                    </>
                );
            })()}
        </Form>
    );
}
