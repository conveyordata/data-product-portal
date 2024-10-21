import { Button, Form, FormProps, Input, Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './platform-service-config-create.module.scss';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useNavigate } from 'react-router-dom';
import { ApplicationPaths } from '@/types/navigation.ts';
import { PLATFORM_SERVICE_CONFIG_MAPPING } from '@/constants/platform-service-config.constants';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';
import { useCreatePlatformServiceConfigMutation } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { useGetAllPlatformServicesQuery } from '@/store/features/platform-services/platform-services-api-slice';
import { useGetAllPlatformsQuery } from '@/store/features/platforms/platforms-api-slice';
import {
    PlatformServiceConfigCreateFormSchema,
    PlatformServiceConfigCreateRequest,
} from '@/types/platform-service-config';
import { useEffect } from 'react';

const { TextArea } = Input;

export function PlatformServiceConfigCreateForm() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const [createPlatformServiceConfig, { isLoading: isCreating }] = useCreatePlatformServiceConfigMutation();
    const { data: platforms = [], isFetching: isFetchingPlatforms } = useGetAllPlatformsQuery();

    const [form] = Form.useForm<PlatformServiceConfigCreateFormSchema>();
    const platformIdFormValue = Form.useWatch('platformId', form);
    const serviceIdFormValue = Form.useWatch('serviceId', form);

    const { data: services = [], isFetching: isFetchingServices } = useGetAllPlatformServicesQuery(
        platformIdFormValue,
        {
            skip: !platformIdFormValue,
        },
    );

    const platformsOptions = platforms.map((platform) => ({ label: platform.name, value: platform.id }));
    const servicesOptions = services.map((service) => ({ label: service.name, value: service.id }));

    const onCancel = () => {
        form.resetFields();
        navigate(ApplicationPaths.PlatformsConfigs);
    };

    const onFinishFailed: FormProps<PlatformServiceConfigCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onFinish: FormProps<PlatformServiceConfigCreateFormSchema>['onFinish'] = async (values) => {
        try {
            const request: PlatformServiceConfigCreateRequest = {
                platformId: values.platformId,
                serviceId: values.serviceId,
                config: JSON.parse(values.config),
            };
            await createPlatformServiceConfig(request).unwrap();
            dispatchMessage({ content: t('Platform Service Configuration created successfully'), type: 'success' });
            navigate(ApplicationPaths.PlatformsConfigs);
        } catch (_e) {
            const errorMessage = t('Failed to create platform service configuration');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const handlePlatformOnSelect = () => {
        form.resetFields(['serviceId', 'config']);
    };

    useEffect(() => {
        if (serviceIdFormValue) {
            const platformName = platforms.find((obj) => obj.id === platformIdFormValue)?.name;
            const serviceName = services.find((obj) => obj.id === serviceIdFormValue)?.name;
            form.setFieldValue(
                'config',
                JSON.stringify(
                    PLATFORM_SERVICE_CONFIG_MAPPING[
                        `${platformName?.toLowerCase()}-${serviceName?.toLocaleLowerCase()}`
                    ] || {},
                    null,
                    4,
                ),
            );
        }
    }, [platformIdFormValue, serviceIdFormValue]);

    return (
        <Form<PlatformServiceConfigCreateFormSchema>
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            labelWrap
            disabled={isFetchingPlatforms || isCreating}
        >
            <Form.Item<PlatformServiceConfigCreateFormSchema>
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
            <Form.Item<PlatformServiceConfigCreateFormSchema>
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
            <Form.Item<PlatformServiceConfigCreateFormSchema>
                name={'config'}
                label={t('Configuration')}
                tooltip={t('A platform service configuration in JSON format')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a platform service configuration in JSON format'),
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
