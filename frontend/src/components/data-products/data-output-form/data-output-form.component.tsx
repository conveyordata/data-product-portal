import { Form, type FormInstance, type FormProps, Input, Radio, Select, Space } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { type RefObject, useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';

import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { NamespaceFormItem } from '@/components/namespace/namespace-form-item';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import {
    useCreateDataOutputMutation,
    useGetDataOutputConfigQuery,
    useGetDataOutputNamespaceLengthLimitsQuery,
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
import { type DataOutputCreateFormSchema, DataOutputStatus } from '@/types/data-output';
import { createDataProductIdPath } from '@/types/navigation';
import type { CustomDropdownItemProps } from '@/types/shared';
import { useDataPlatforms } from '@/utils/data-platforms';
import { selectFilterOptionByLabel } from '@/utils/form.helper';

import styles from './data-output-form.module.scss';
import { DynamicDataOutputForm } from './dynamic-data-output-form.component';

type Props = {
    mode: 'create';
    formRef: RefObject<FormInstance<DataOutputCreateFormSchema> | null>;
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
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(dataProductId);
    const { data: availableTags, isFetching: isFetchingTags } = useGetAllTagsQuery();
    const { data: platformConfig, isLoading: platformsLoading } = useGetAllPlatformsConfigsQuery();
    const { data: outputYamlConfig, isLoading: isFetchingOutputYamlConfig } = useGetDataOutputConfigQuery(undefined);
    // Mutations
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();

    // State
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps<string> | undefined>(
        undefined,
    );
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps<string> | undefined>(
        undefined,
    );
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

    const isLoading =
        platformsLoading || isCreating || isFetchingInitialValues || isFetchingTags || isFetchingOutputYamlConfig;

    const tagSelectOptions = availableTags?.map((tag) => ({ label: tag.value, value: tag.id })) ?? [];
    const platforms = useDataPlatforms(outputYamlConfig, t);
    const dataPlatforms = useMemo(
        () =>
            outputYamlConfig
                ? platforms
                      // Configured platforms
                      .filter(
                          (platform) =>
                              platform.hasConfig &&
                              platformConfig?.some((config) => config.platform.name === platform.label),
                      )
                      // Configured services
                      .map((platform) => {
                          const platformConfigs = platformConfig?.filter(
                              (config) => config.platform.name === platform.label,
                          );
                          platform.children = platform.children?.filter((child) =>
                              platformConfigs?.some((config) => config.service.name === child.label),
                          );
                          return platform;
                      })
                : [],
        [platformConfig, outputYamlConfig, platforms],
    );

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

    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (!isLoading) {
                await createDataOutput({ id: dataProductId, dataOutput: values }).unwrap();
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

    const onDataPlatformClick = (dropdown: CustomDropdownItemProps<string>) => {
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

    const onConfigurationClick = (dropdown: CustomDropdownItemProps<string>) => {
        if (!isLoading) {
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
            <NamespaceFormItem
                form={form}
                tooltip={t('The namespace of the data output')}
                max_length={namespaceLengthLimits?.max_length}
                canEditNamespace={canEditNamespace}
                toggleCanEditNamespace={() => setCanEditNamespace((prev) => !prev)}
                validationRequired
                validateNamespace={validateNamespaceCallback}
            />
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
            <Form.Item<DataOutputCreateFormSchema> name={'tag_ids'} label={t('Tags')} initialValue={[]}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select data output tags')}
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
            {currentDataProduct && selectedConfiguration && (
                <DynamicDataOutputForm
                    form={form}
                    namespace={currentDataProduct.namespace}
                    sourceAligned={sourceAligned}
                    platform={selectedConfiguration.value}
                    identifiers={identifiers}
                />
            )}
        </Form>
    );
}
