import { Form, type FormInstance, type FormProps, Input, Radio, Select, Space } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { type RefObject, useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';

import awsLogo from '@/assets/icons/aws-logo.svg?react';
import redshiftLogo from '@/assets/icons/aws-redshift-logo.svg?react';
import databricksLogo from '@/assets/icons/databricks-logo.svg?react';
import glueLogo from '@/assets/icons/glue-logo.svg?react';
import s3Logo from '@/assets/icons/s3-logo.svg?react';
import snowflakeLogo from '@/assets/icons/snowflake-logo.svg?react';
import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import {
    useCreateDataOutputMutation,
    useGetDataOutputNamespaceLengthLimitsQuery,
    useGetDataOutputUIElementMetadataQuery,
    useLazyGetDataOutputNamespaceSuggestionQuery,
    useLazyGetDataOutputResultStringQuery,
} from '@/store/features/data-outputs/data-outputs-api-slice';
import {
    useGetDataProductByIdQuery,
    useLazyValidateDataOutputNamespaceQuery,
} from '@/store/features/data-products/data-products-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { useGetAllPlatformsConfigsQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { useGetAllTagsQuery } from '@/store/features/tags/tags-api-slice';
import { type DataOutputConfiguration, type DataOutputCreateFormSchema, DataOutputStatus } from '@/types/data-output';
import type { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { createDataProductIdPath } from '@/types/navigation';
import type { CustomDropdownItemProps } from '@/types/shared';
import { getDataPlatforms } from '@/utils/data-platforms';
import { selectFilterOptionByLabel } from '@/utils/form.helper';

import styles from './data-output-form.module.scss';
import { GenericDataOutputForm } from './generic-data-output-form.component';

type Props = {
    mode: 'create';
    formRef: RefObject<FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration> | null>;
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
    const { data: uiMetadataGroups, isLoading: isLoadingMetadata } = useGetDataOutputUIElementMetadataQuery();
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(dataProductId);
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const { data: platformConfig, isLoading: platformsLoading } = useGetAllPlatformsConfigsQuery();

    // Mutations
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();

    // State
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<
        CustomDropdownItemProps<DataPlatforms> | undefined
    >(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<
        CustomDropdownItemProps<DataPlatforms> | undefined
    >(undefined);
    const [identifiers, setIdentifiers] = useState<string[] | undefined>(undefined);

    // Form
    const [form] = Form.useForm();
    const sourceAligned = Form.useWatch('sourceAligned', form);
    const dataOutputNameValue = Form.useWatch('name', form);

    // Namespace validation
    const [fetchNamespace, { data: namespaceSuggestion }] = useLazyGetDataOutputNamespaceSuggestionQuery();
    const [validateNamespace] = useLazyValidateDataOutputNamespaceQuery();
    const { data: namespaceLengthLimits } = useGetDataOutputNamespaceLengthLimitsQuery();
    const [canEditNamespace, setCanEditNamespace] = useState<boolean>(false);

    // Result string
    const [fetchResultString] = useLazyGetDataOutputResultStringQuery();

    const isLoading = platformsLoading || isCreating || isFetchingInitialValues || isFetchingTags;

    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];

    // Build platform tiles dynamically from metadata
    const dataPlatforms = useMemo(() => {
        if (!uiMetadataGroups || !platformConfig) {
            return [];
        }

        // Icon mapping
        const iconMap: Record<string, any> = {
            's3-logo.svg': s3Logo,
            'aws-redshift-logo.svg': redshiftLogo,
            'glue-logo.svg': glueLogo,
            'snowflake-logo.svg': snowflakeLogo,
            'databricks-logo.svg': databricksLogo,
            'aws-logo.svg': awsLogo,
        };

        // Group by parent platform
        const parentPlatforms = new Map<string, CustomDropdownItemProps<DataPlatform>>();
        const childPlatforms = new Map<string, CustomDropdownItemProps<DataPlatform>[]>();

        uiMetadataGroups.forEach((meta) => {
            // Only include platforms that have config
            const hasConfig = platformConfig.some(
                (config) => config.service.name.toLowerCase() === meta.display_name.toLowerCase(),
            );

            if (!hasConfig) {
                return;
            }

            const platformItem: CustomDropdownItemProps<DataPlatform> = {
                label: t(meta.display_name),
                value: meta.platform as DataPlatform,
                icon: iconMap[meta.icon_name] || iconMap['s3-logo.svg'],
                hasMenu: true,
                hasConfig: true,
                children: [],
            };

            if (meta.parent_platform) {
                // This is a child platform
                if (!childPlatforms.has(meta.parent_platform)) {
                    childPlatforms.set(meta.parent_platform, []);
                }
                childPlatforms.get(meta.parent_platform)!.push(platformItem);

                // Ensure parent exists
                if (!parentPlatforms.has(meta.parent_platform)) {
                    parentPlatforms.set(meta.parent_platform, {
                        label: t(meta.parent_platform.toUpperCase()),
                        value: meta.parent_platform as DataPlatform,
                        icon: iconMap[`${meta.parent_platform}-logo.svg`] || iconMap['aws-logo.svg'],
                        hasMenu: true,
                        hasConfig: true,
                        children: [],
                    });
                }
            } else {
                // This is a top-level platform
                if (!parentPlatforms.has(meta.platform)) {
                    parentPlatforms.set(meta.platform, platformItem);
                }
            }
        });

        // Attach children to parents
        parentPlatforms.forEach((parent, key) => {
            if (childPlatforms.has(key)) {
                parent.children = childPlatforms.get(key);
            }
        });

        return Array.from(parentPlatforms.values());
    }, [uiMetadataGroups, platformConfig, t]);

    const dataPlatformsOld = useMemo(
        () =>
            getDataPlatforms(t)
                // Configured platforms
                .filter(
                    (platform) =>
                        platform.hasConfig && platformConfig?.some((config) => config.platform.name === platform.label),
                )
                // Configured services
                .map((platform) => {
                    const platformConfigs = platformConfig?.filter((config) => config.platform.name === platform.label);
                    platform.children = platform.children?.filter((child) =>
                        platformConfigs?.some((config) => config.service.name === child.label),
                    );
                    return platform;
                }),
        [platformConfig, t],
    );

    const platformServiceConfigMap = useMemo(() => {
        const map = new Map<DataPlatform, ServiceConfig>();

        if (!platformConfig) {
            return map;
        }
        for (const config of platformConfig) {
            const platform = (
                config.platform.name === config.service.name ? config.platform.name : config.service.name
            ).toLocaleLowerCase() as DataPlatform;

            map.set(platform, {
                platform_id: config.platform.id,
                service_id: config.service.id,
                configuration: config.config,
            });
        }

        return map;
    }, [platformConfig]);

    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (!platformsLoading) {
                await createDataOutput({ id: dataProductId, dataOutput: values }).unwrap();
                dispatchMessage({ content: t('Technical asset created successfully'), type: 'success' });
                modalCallbackOnSubmit();
                navigate(createDataProductIdPath(dataProductId, TabKeys.DataOutputs));

                form.resetFields();
            }
        } catch (_e) {
            const errorMessage = 'Failed to create technical asset';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataOutputCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onDataPlatformClick = (dropdown: CustomDropdownItemProps<DataPlatforms>) => {
        if (selectedDataPlatform !== dropdown) {
            form.setFieldsValue({ configuration: undefined, result: undefined });
            setSelectedDataPlatform(dropdown);

            if (dropdown.children?.length === 0) {
                setSelectedConfiguration(dropdown);
                form.setFieldValue('service_id', platformServiceConfigMap.get(dropdown.value)?.service_id);
                setIdentifiers(platformServiceConfigMap.get(dropdown.value)?.configuration);
            } else {
                setSelectedConfiguration(undefined);
                setIdentifiers(undefined);
            }
        }
    };

    const onConfigurationClick = (dropdown: CustomDropdownItemProps<DataPlatforms>) => {
        if (!platformsLoading) {
            if (selectedConfiguration !== dropdown) {
                form.setFieldsValue({ configuration: undefined, result: undefined });
                setSelectedConfiguration(dropdown);
                setIdentifiers(platformServiceConfigMap.get(dropdown.value)?.configuration);
            }
        }
    };

    // Namespace validation
    const fetchNamespaceDebounced = useDebouncedCallback((name: string) => fetchNamespace(name), DEBOUNCE);

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
            form.setFieldValue('namespace', namespaceSuggestion?.namespace);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditNamespace, namespaceSuggestion]);

    const options = [
        { label: t('Product aligned'), value: false },
        { label: t('Source aligned'), value: true },
    ];

    const validateNamespaceCallback = useCallback(
        (namespace: string) => validateNamespace({ dataProductId, namespace }).unwrap(),
        [validateNamespace, dataProductId],
    );

    // Result string
    const setResultString = useDebouncedCallback((values: DataOutputCreateFormSchema) => {
        form.validateFields(['configuration'], { validateOnly: true, recursive: true })
            .then(() => {
                const request = {
                    platform_id: values.platform_id,
                    service_id: values.service_id,
                    configuration: values.configuration,
                };
                return fetchResultString(request).unwrap();
            })
            .then((result) => form.setFieldValue('result', result))
            .catch(() => form.setFieldValue('result', undefined));
    }, DEBOUNCE);

    const onValuesChange: FormProps<DataOutputCreateFormSchema>['onValuesChange'] = (
        changed,
        values: DataOutputCreateFormSchema,
    ) => {
        if (changed.configuration || (values.configuration && changed.sourceAligned)) {
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
                tooltip={t('The name of your technical asset')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the technical asset'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <NamespaceFormItem
                form={form}
                tooltip={t('The namespace of the technical asset')}
                max_length={namespaceLengthLimits?.max_length}
                canEditNamespace={canEditNamespace}
                toggleCanEditNamespace={() => setCanEditNamespace((prev) => !prev)}
                validationRequired
                validateNamespace={validateNamespaceCallback}
            />
            <Form.Item<DataOutputCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the technical asset')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the technical asset'),
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
                    placeholder={t('Select technical asset tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    filterOption={selectFilterOptionByLabel}
                />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema>
                name={'status'}
                required
                hidden
                initialValue={DataOutputStatus.Active}
            />
            <Form.Item<DataOutputCreateFormSchema>
                name={'sourceAligned'}
                label={t('Alignment')}
                required
                tooltip={t(
                    'If you follow product thinking approach, select Product aligned. If you want more freedom, you can select Source aligned, however this request will need to be approved by administrators. By default, or when in doubt, leave product aligned selected.',
                )}
                initialValue={false}
            >
                <Select allowClear={false} options={options} />
            </Form.Item>
            <Form.Item name={'platform_id'}>
                <Radio.Group>
                    <Space wrap className={styles.radioButtonContainer}>
                        {dataPlatforms.map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
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
                            <DataOutputPlatformTile<DataPlatform>
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
                    <GenericDataOutputForm
                        form={form}
                        uiMetadataGroups={pluginMetadata.ui_metadata}
                        namespace={currentDataProduct.namespace}
                        identifiers={identifiers}
                        sourceAligned={sourceAligned}
                        configurationType={pluginMetadata.plugin}
                        resultLabel={pluginMetadata.result_label}
                        resultTooltip={pluginMetadata.result_tooltip}
                    />
                );
            })()}
        </Form>
    );
}
