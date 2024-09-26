import { Typography, Form, Input, Collapse, Row, Col, Button, Select, Progress, Switch } from 'antd';
import { useTranslation } from 'react-i18next';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import React from 'react';
import { useModal } from '@/hooks/use-modal.tsx';
import { AddPlatformPopup } from './components/popup/add-platform-popup';
import { AWSS3Config } from './components/configurations/aws/s3-config';
import { AWSGlueConfig } from './components/configurations/aws/glue-config';
import { IdName } from '@/types/shared';

const serviceComponent: { [key: string]: React.ComponentType<any> } = {
    'aws-s3': AWSS3Config,
    'aws-glue': AWSGlueConfig,
};

export const Settings = () => {
    const { isVisible, handleOpen, handleClose } = useModal();
    const { t } = useTranslation();

    const [form] = Form.useForm();

    const configuration = { platforms: [], environments: [] };

    const formPlatforms = Form.useWatch('platforms', form);

    // if (configuration.isLoading) {
    //     return <Progress percent={50} status="active" />;
    // }

    type ServiceSchema = IdName & {
        identifiers: string[];
    };

    type PlatformSchema = IdName & {
        services: ServiceSchema[];
    };

    type ServiceConfiguration = {
        service_name: string;
        service_id: string;
        configs: { identifier: string }[];
    };

    type PlatformServiceSetting = {
        platform_name: string;
        platform_id: string;
        account_id: string;
        region: string;
        services: ServiceConfiguration[];
    };

    type EnvironmentSchema = {
        name: string;
        settings: PlatformServiceSetting[];
    };

    const addEnvironment = () => {
        const platforms: PlatformSchema[] = form.getFieldValue('platforms');

        const envSetting = platforms.map((platform) => ({
            platform_name: platform.name,
            platform_id: platform.id,
            services: platform.services
                .map((service: ServiceSchema) => ({
                    service_name: service.name,
                    service_id: service.id,
                    configs: service.identifiers.map((identifier: string) => ({ identifier })),
                }))
                .filter((service) => service.configs.length > 0),
        }));

        return {
            // settings: envSetting.filter((setting: PlatformServiceSetting) => setting.configs.length > 0),
            settings: envSetting,
        };
    };

    const handleIdentifiers = (identifiers: string[], platform, service) => {
        const environments: EnvironmentSchema[] = form.getFieldValue('environments');

        const updatedEnvs = environments.map((environment: EnvironmentSchema) => {
            const currentPlatform: IdName = form.getFieldValue(['platforms', platform.name]);

            const currentService: IdName = form.getFieldValue(['platforms', platform.name, 'services', service.name]);

            const filteredPlatformSetting = environment.settings.find(
                (setting) => setting.platform_id === currentPlatform.id,
            ) || {
                platform_name: currentPlatform.name,
                platform_id: currentPlatform.id,
                services: [],
            };

            const filteredService = filteredPlatformSetting.services.find(
                (service) => service.service_id === currentService.id,
            ) || {
                service_name: currentService.name,
                service_id: currentService.id,
                configs: [],
            };

            const newServiceConfigs = identifiers.map((identifier) => {
                const existsConfig = filteredService.configs.find((config: any) => config.identifier === identifier);

                if (existsConfig) return existsConfig;

                return {
                    identifier: identifier,
                };
            });

            const newService =
                newServiceConfigs.length > 0
                    ? {
                          ...filteredService,
                          configs: newServiceConfigs,
                      }
                    : undefined;

            const filteredServices = filteredPlatformSetting.services.filter(
                (service) => service.service_id !== currentService.id,
            );

            const newServices = [newService, ...filteredServices].filter(Boolean);

            const newPlaformSetting =
                newServices.length > 0
                    ? {
                          ...filteredPlatformSetting,
                          services: newServices,
                      }
                    : undefined;

            const filteredSettings = environment.settings.filter(
                (setting) => setting.platform_id !== currentPlatform.id,
            );

            const newSettings = [newPlaformSetting, ...filteredSettings].filter(Boolean);

            const environmentObject = {
                ...environment,
                settings: newSettings,
            };

            return environmentObject;
        });

        form.setFieldValue('environments', updatedEnvs);

        return identifiers;
    };

    return (
        <>
            <Form
                layout="vertical"
                form={form}
                labelCol={FORM_GRID_WRAPPER_COLS}
                wrapperCol={FORM_GRID_WRAPPER_COLS}
                initialValues={configuration}
                // initialValues={{
                //     platforms: [
                //         {
                //             name: 'AWS',
                //             id: '8e99f3e5-5c12-4800-9c21-42cb429f20b3',
                //             services: [
                //                 {
                //                     name: 'S3',
                //                     id: 'f503376c-fc49-40e3-8a3d-ee80804e0fe4',
                //                     identifiers: ['s3'],
                //                 },
                //                 // {
                //                 //     name: 'Glue',
                //                 //     id: 'c62a7401-23d9-4dd6-9885-f5b8f5cf760b',
                //                 //     identifiers: ['glue'],
                //                 // },
                //             ],
                //         },
                //     ],
                //     environments: [
                //         {
                //             name: 'development',
                //             settings: [
                //                 {
                //                     platform_name: 'AWS',
                //                     platform_id: '8e99f3e5-5c12-4800-9c21-42cb429f20b3',
                //                     account_id: '111111111',
                //                     region: 'us-east',
                //                     services: [
                //                         {
                //                             service_name: 'S3',
                //                             service_id: 'f503376c-fc49-40e3-8a3d-ee80804e0fe4',
                //                             configs: [
                //                                 {
                //                                     identifier: 's3',
                //                                     bucket_name: 'bucketName',
                //                                     arn: 'dfd',
                //                                     kms_key: 'kmsKey',
                //                                     is_default: true,
                //                                 },
                //                             ],
                //                         },
                //                         // {
                //                         //     service_name: 'Glue',
                //                         //     service_id: 'c62a7401-23d9-4dd6-9885-f5b8f5cf760b',
                //                         //     configs: [
                //                         //         {
                //                         //             identifier: 'glue',
                //                         //             bucket_identifier: 'bucketName',
                //                         //             database: 'dbName',
                //                         //             s3_path: 's3Path',
                //                         //         },
                //                         //     ],
                //                         // },
                //                     ],
                //                 },
                //             ],
                //         },
                //     ],
                // }}
                onFinish={(values) => console.log(JSON.stringify(values, null, 2))}
            >
                <Typography.Title level={2}>Platforms</Typography.Title>

                <Form.Item>
                    <Button type="dashed" onClick={handleOpen} icon={<PlusOutlined />}>
                        Add platform/service
                    </Button>
                </Form.Item>

                <Form.List name={['platforms']}>
                    {(platforms) => (
                        <div>
                            <Form.Item>
                                <Collapse
                                    items={platforms.map((platform) => ({
                                        key: platform.key,
                                        label: form.getFieldValue(['platforms', platform.name]).name,
                                        children: (
                                            <div>
                                                <Form.List name={[platform.name, 'services']}>
                                                    {(services, servicesHelpers) => (
                                                        <>
                                                            {services.map((service) => (
                                                                <div
                                                                    key={service.key}
                                                                    style={{
                                                                        border: '1px solid lightgray',
                                                                        borderRadius: 8,
                                                                        padding: 24,
                                                                        marginBottom: 24,
                                                                    }}
                                                                >
                                                                    <Typography.Title level={5}>
                                                                        {form.getFieldValue([
                                                                            'platforms',
                                                                            platform.name,
                                                                            'services',
                                                                            service.key,
                                                                            'name',
                                                                        ])}
                                                                    </Typography.Title>
                                                                    <Form.Item
                                                                        {...service}
                                                                        name={[service.key, 'identifiers']}
                                                                        label="Identifiers"
                                                                        rules={[
                                                                            {
                                                                                required: true,
                                                                                message: 'Please enter a value',
                                                                            },
                                                                        ]}
                                                                        getValueFromEvent={(identifiers: string[]) =>
                                                                            handleIdentifiers(
                                                                                identifiers,
                                                                                platform,
                                                                                service,
                                                                            )
                                                                        }
                                                                    >
                                                                        <Select
                                                                            mode="tags"
                                                                            open={false}
                                                                            suffixIcon={null}
                                                                        />
                                                                    </Form.Item>
                                                                </div>
                                                            ))}
                                                        </>
                                                    )}
                                                </Form.List>
                                            </div>
                                        ),
                                    }))}
                                />
                            </Form.Item>
                        </div>
                    )}
                </Form.List>

                <Typography.Title level={2}>Environments</Typography.Title>
                <Form.List name={['environments']}>
                    {(environments, environmentsHelpers) => (
                        <>
                            {environments.map((environment) => (
                                <Form.Item
                                    style={{
                                        padding: 16,
                                        borderRadius: 8,
                                        border: '2px solid #4D918B',
                                    }}
                                    key={environment.key}
                                >
                                    <Row align="middle" gutter={24}>
                                        <Col xs={20}>
                                            <Form.Item
                                                name={[environment.name, 'name']}
                                                label="Environment"
                                                rules={[
                                                    {
                                                        required: true,
                                                        message: 'Please enter an environment name',
                                                    },
                                                ]}
                                            >
                                                <Input />
                                            </Form.Item>
                                        </Col>
                                        <Col xs={4}>
                                            <MinusCircleOutlined
                                                onClick={() => environmentsHelpers.remove(environment.name)}
                                                style={{ fontSize: '32px' }}
                                            />
                                        </Col>
                                    </Row>
                                    <Form.Item
                                        name={[environment.name, 'is_default']}
                                        valuePropName="checked"
                                        label={t('Default environment')}
                                    >
                                        <Switch checkedChildren="Yes" unCheckedChildren="No" />
                                    </Form.Item>

                                    <Typography.Title level={3}>Settings</Typography.Title>
                                    <Form.List name={[environment.name, 'settings']}>
                                        {(settings) =>
                                            settings.map((setting) => (
                                                <Form.Item key={setting.key}>
                                                    <div
                                                        style={{
                                                            padding: 16,
                                                            borderRadius: 8,
                                                            border: '2px solid gray',
                                                        }}
                                                    >
                                                        <div style={{ textAlign: 'center' }}>
                                                            <Typography.Title level={3}>
                                                                {form.getFieldValue([
                                                                    'environments',
                                                                    environment.name,
                                                                    'settings',
                                                                    setting.name,
                                                                    'platform_name',
                                                                ])}
                                                            </Typography.Title>
                                                        </div>

                                                        <Form.Item
                                                            name={[setting.name, 'account_id']}
                                                            label="Account ID"
                                                            rules={[
                                                                {
                                                                    required: true,
                                                                    message: 'Please enter an account id',
                                                                },
                                                            ]}
                                                        >
                                                            <Input />
                                                        </Form.Item>

                                                        <Form.Item
                                                            name={[setting.name, 'region']}
                                                            label="Region"
                                                            rules={[
                                                                {
                                                                    required: true,
                                                                    message: 'Please enter a region',
                                                                },
                                                            ]}
                                                        >
                                                            <Input />
                                                        </Form.Item>

                                                        <Form.List name={[setting.name, 'services']}>
                                                            {(services) =>
                                                                services.map((service) => (
                                                                    <div
                                                                        style={{
                                                                            padding: 16,
                                                                            marginBottom: 10,
                                                                            borderRadius: 8,
                                                                            border: '3px dashed lightgray',
                                                                        }}
                                                                    >
                                                                        <div style={{ textAlign: 'center' }}>
                                                                            <Typography.Title level={4}>
                                                                                {form.getFieldValue([
                                                                                    'environments',
                                                                                    environment.name,
                                                                                    'settings',
                                                                                    setting.name,
                                                                                    'services',
                                                                                    service.name,
                                                                                    'service_name',
                                                                                ])}
                                                                            </Typography.Title>
                                                                        </div>

                                                                        <Row gutter={16}>
                                                                            <Form.List name={[service.name, 'configs']}>
                                                                                {(configs) =>
                                                                                    configs.map((conf) => {
                                                                                        const platformName =
                                                                                            form.getFieldValue([
                                                                                                'environments',
                                                                                                environment.name,
                                                                                                'settings',
                                                                                                setting.name,
                                                                                                'platform_name',
                                                                                            ]);

                                                                                        const serviceName =
                                                                                            form.getFieldValue([
                                                                                                'environments',
                                                                                                environment.name,
                                                                                                'settings',
                                                                                                setting.name,
                                                                                                'services',
                                                                                                service.name,
                                                                                                'service_name',
                                                                                            ]);

                                                                                        const DynamicComponent =
                                                                                            serviceComponent[
                                                                                                `${platformName.toLowerCase()}-${serviceName.toLowerCase()}`
                                                                                            ];

                                                                                        const identifier =
                                                                                            form.getFieldValue([
                                                                                                'environments',
                                                                                                environment.name,
                                                                                                'settings',
                                                                                                setting.name,
                                                                                                'services',
                                                                                                service.name,
                                                                                                'configs',
                                                                                                conf.name,
                                                                                                'identifier',
                                                                                            ]);

                                                                                        return (
                                                                                            <DynamicComponent
                                                                                                key={conf.key}
                                                                                                config={conf}
                                                                                                identifier={identifier}
                                                                                            />
                                                                                        );
                                                                                    })
                                                                                }
                                                                            </Form.List>
                                                                        </Row>
                                                                    </div>
                                                                ))
                                                            }
                                                        </Form.List>
                                                    </div>
                                                </Form.Item>
                                            ))
                                        }
                                    </Form.List>
                                </Form.Item>
                            ))}
                            <Form.Item>
                                <Button
                                    type="dashed"
                                    onClick={() => environmentsHelpers.add(addEnvironment())}
                                    icon={<PlusOutlined />}
                                    disabled={formPlatforms?.length > 0 ? false : true}
                                >
                                    Add environment
                                </Button>
                            </Form.Item>
                        </>
                    )}
                </Form.List>
                <Row justify="end">
                    <Col xs={4}>
                        <Button
                            block
                            type="primary"
                            htmlType="submit"
                            // disabled={formPlatforms?.length > 0 && environments?.length > 0 ? false : true}
                        >
                            Save
                        </Button>
                    </Col>
                </Row>
            </Form>
            {isVisible && <AddPlatformPopup onClose={handleClose} isOpen={isVisible} settingsForm={form} />}
        </>
    );
};
