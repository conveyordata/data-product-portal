import { Button, Form, type FormProps, Input, Select, Space } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

import { buildUrl } from '@/api/api-urls';
import { ENV_PLATFORM_SERVICE_CONFIG_MAPPING } from '@/constants/environment-config.constants.ts';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { useCreateEnvPlatformServiceConfigMutation } from '@/store/features/environments/environments-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetPlatformServiceConfigQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { useGetAllPlatformServicesQuery } from '@/store/features/platform-services/platform-services-api-slice';
import { useGetAllPlatformsQuery } from '@/store/features/platforms/platforms-api-slice';
import { EnvironmentConfigCreateFormSchema, EnvironmentConfigCreateRequest } from '@/types/environment';
import { ApplicationPaths } from '@/types/navigation.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';

import styles from './environment-config-create.module.scss';

const { TextArea } = Input;

export function EnvironmentConfigCreateForm() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { environmentId = '' } = useParams();

    const [createEnvPlatformServiceConfig, { isLoading: isCreating }] = useCreateEnvPlatformServiceConfigMutation();
    const { data: platforms = [], isFetching: isFetchingPlatforms } = useGetAllPlatformsQuery();

    const [form] = Form.useForm<EnvironmentConfigCreateFormSchema>();
    const platformIdFormValue = Form.useWatch('platformId', form);
    const serviceIdFormValue = Form.useWatch('serviceId', form);

    const { data: services = [], isFetching: isFetchingServices } = useGetAllPlatformServicesQuery(
        platformIdFormValue,
        {
            skip: !platformIdFormValue,
        },
    );

    const { data: platformServiceConfig } = useGetPlatformServiceConfigQuery(
        {
            platformId: platformIdFormValue,
            serviceId: serviceIdFormValue,
        },
        { skip: !platformIdFormValue || !serviceIdFormValue },
    );

    const platformsOptions = platforms.map((platform) => ({ label: platform.name, value: platform.id }));
    const servicesOptions = services.map((service) => ({ label: service.name, value: service.id }));

    const onCancel = () => {
        form.resetFields();
        navigate(buildUrl(ApplicationPaths.EnvironmentConfigs, { environmentId }));
    };

    const onFinishFailed: FormProps<EnvironmentConfigCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onFinish: FormProps<EnvironmentConfigCreateFormSchema>['onFinish'] = async (values) => {
        try {
            const body: EnvironmentConfigCreateRequest = {
                platform_id: values.platformId,
                service_id: values.serviceId,
                config: JSON.parse(values.config),
            };
            await createEnvPlatformServiceConfig({ environmentId, body }).unwrap();
            dispatchMessage({ content: t('Environment Configuration created successfully'), type: 'success' });
            navigate(buildUrl(ApplicationPaths.EnvironmentConfigs, { environmentId }));
        } catch (_e) {
            const errorMessage = t('Failed to create environment configuration');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const handlePlatformOnSelect = () => {
        form.resetFields(['serviceId', 'identifiers', 'config']);
    };

    useEffect(() => {
        if (platformServiceConfig) {
            const configTemplateName = `${platformServiceConfig.platform.name.toLowerCase()}-${platformServiceConfig.service.name.toLocaleLowerCase()}`;
            const identifiers = platformServiceConfig.config.identifiers;
            const configTemplate = identifiers.reduce(
                (acc, identifier) => {
                    acc[identifier] = ENV_PLATFORM_SERVICE_CONFIG_MAPPING[configTemplateName];
                    return acc;
                },
                {} as Record<string, object>,
            );
            form.setFieldValue('identifiers', identifiers.join(', '));
            form.setFieldValue('config', JSON.stringify(configTemplate, null, 4));
        }
    }, [form, platformServiceConfig]);

    return (
        <Form<EnvironmentConfigCreateFormSchema>
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete={'off'}
            requiredMark={false}
            labelWrap
            disabled={isFetchingPlatforms || isCreating}
        >
            <Form.Item<EnvironmentConfigCreateFormSchema>
                name={'platformId'}
                label={t('Platform')}
                rules={[
                    {
                        required: true,
                        message: t('Please select a platform'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingPlatforms}
                    options={platformsOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                    allowClear
                    onSelect={handlePlatformOnSelect}
                />
            </Form.Item>
            <Form.Item<EnvironmentConfigCreateFormSchema>
                name={'serviceId'}
                label={t('Service')}
                rules={[
                    {
                        required: true,
                        message: t('Please select a service'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingServices}
                    options={servicesOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                    allowClear
                    showSearch
                    disabled={!platformIdFormValue || isFetchingServices}
                />
            </Form.Item>

            <Form.Item<EnvironmentConfigCreateFormSchema> name="identifiers" label={t('Identifiers')}>
                <Input disabled />
            </Form.Item>

            <Form.Item<EnvironmentConfigCreateFormSchema>
                name={'config'}
                label={t('Configuration')}
                tooltip={t('An environment configuration in JSON format')}
                rules={[
                    {
                        required: true,
                        message: t('Please input an environment configuration in JSON format'),
                    },
                ]}
            >
                <TextArea autoSize={{ minRows: 5 }} />
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreating}
                        disabled={isFetchingPlatforms || !platformIdFormValue || isFetchingServices}
                    >
                        {t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isCreating}
                        disabled={isFetchingServices || isFetchingServices}
                    >
                        {t('Cancel')}
                    </Button>
                </Space>
            </Form.Item>
        </Form>
    );
}
