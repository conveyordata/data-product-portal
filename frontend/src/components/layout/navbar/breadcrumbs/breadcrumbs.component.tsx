import Icon, { HomeOutlined, SettingOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { Breadcrumb, Space, Typography } from 'antd';
import { BreadcrumbItemType, BreadcrumbSeparatorType } from 'antd/es/breadcrumb/Breadcrumb';
import { ReactNode, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router';

import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { BreadcrumbLink } from '@/components/layout/navbar/breadcrumbs/breadcrumb-link/breadcrumb-link.component.tsx';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import {
    useGetEnvConfigByIdQuery,
    useGetEnvironmentByIdQuery,
} from '@/store/features/environments/environments-api-slice';
import { useGetPlatformServiceConfigByIdQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { ApplicationPaths, createEnvironmentConfigsPath, DynamicPathParams } from '@/types/navigation.ts';
import {
    isDataOutputEditPage,
    isDataProductEditPage,
    isEnvConfigPage,
    isEnvironmentConfigCreatePage,
    isEnvironmentConfigsPage,
} from '@/utils/routes.helper.ts';

import styles from './breadcrumbs.module.scss';

type BreadcrumbType = Partial<BreadcrumbItemType & BreadcrumbSeparatorType> & { icon?: ReactNode };

export const Breadcrumbs = () => {
    const { t } = useTranslation();
    const { pathname } = useLocation();
    const params = useParams<DynamicPathParams>();
    const pathnames = useMemo(
        () => (pathname === ApplicationPaths.Home ? [ApplicationPaths.Home] : pathname.split('/').filter((x) => x)),
        [pathname],
    );
    const {
        dataProductId = '',
        datasetId = '',
        platformServiceConfigId = '',
        environmentId = '',
        envConfigId = '',
        dataOutputId = '',
    } = params;
    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductByIdQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { data: dataOutput, isFetching: isFetchingDataOutput } = useGetDataOutputByIdQuery(dataOutputId, {
        skip: !dataOutputId,
    });
    const { data: dataset, isFetching: isFetchingDataset } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const { data: platformServiceConfig, isFetching: isFetchingPlatformServiceConfig } =
        useGetPlatformServiceConfigByIdQuery(platformServiceConfigId, { skip: !platformServiceConfigId });
    const { data: environment, isFetching: isFetchingEnvironment } = useGetEnvironmentByIdQuery(environmentId, {
        skip: !environmentId,
    });
    const { data: envConfig, isFetching: isFetchingEnvConfig } = useGetEnvConfigByIdQuery(envConfigId, {
        skip: !envConfigId,
    });

    const items: BreadcrumbType[] = useMemo(
        () =>
            [
                {
                    type: 'separator',
                    separator: (
                        <BreadcrumbLink
                            to={ApplicationPaths.Home}
                            title={undefined}
                            separator={
                                <Space
                                    classNames={{
                                        item: styles.breadcrumbItem,
                                    }}
                                >
                                    /
                                </Space>
                            }
                            icon={<HomeOutlined />}
                        />
                    ),
                },
                ...pathnames.map((pathname, index) => {
                    const path =
                        pathname === ApplicationPaths.Home ? pathname : `/${pathnames.slice(0, index + 1).join('/')}`;

                    const breadcrumbItem: Partial<BreadcrumbItemType> = {
                        path,
                        title: pathname,
                    };

                    switch (path) {
                        case ApplicationPaths.Home:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        <HomeOutlined />
                                        {t('Home')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.DataProducts:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        <Icon component={dataProductOutlineIcon} />
                                        {t('Data Products')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.DataProductNew:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        {t('New Data Product')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.Datasets:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        <Icon component={datasetOutlineIcon} />
                                        {t('Marketplace')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.DatasetNew:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        {t('New Dataset')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.AuditLogs:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        <UnorderedListOutlined />
                                        {t('Audit Logs')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.PlatformsConfigs:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space classNames={{ item: styles.breadcrumbItem }}>
                                        <SettingOutlined />
                                        {t('Platforms Configurations')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.Environments:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space classNames={{ item: styles.breadcrumbItem }}>
                                        <SettingOutlined />
                                        {t('Environments')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.EnvironmentNew:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        {t('New Environment')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.Settings:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        {t('Settings')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.PlatformServiceConfigNew:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        {t('New Platform Service Configuration')}
                                    </Space>
                                ),
                            });
                            break;
                        case ApplicationPaths.RoleConfiguration:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        {t('Role Management')}
                                    </Space>
                                ),
                            });
                            break;
                        default:
                            Object.assign(breadcrumbItem, {
                                title: '',
                            });

                            // Case for data product and dataset
                            if (dataProductId && dataProduct && !isFetchingDataProduct) {
                                if (
                                    isDataProductEditPage(path, dataProductId) ||
                                    isDataOutputEditPage(path, dataOutputId, dataProductId)
                                ) {
                                    Object.assign(breadcrumbItem, {
                                        title: (
                                            <Space
                                                classNames={{
                                                    item: styles.breadcrumbItem,
                                                }}
                                            >
                                                {t('Edit')}
                                            </Space>
                                        ),
                                    });
                                } else {
                                    if (
                                        dataOutputId &&
                                        dataOutput &&
                                        !isFetchingDataOutput &&
                                        path.split('/').length == 4
                                    ) {
                                        Object.assign(breadcrumbItem, {
                                            title: (
                                                <Typography.Text
                                                    ellipsis={{ tooltip: dataOutput.name }}
                                                    rootClassName={styles.title}
                                                >
                                                    {dataOutput.name}
                                                </Typography.Text>
                                            ),
                                        });
                                    } else {
                                        Object.assign(breadcrumbItem, {
                                            title: (
                                                <Typography.Text
                                                    ellipsis={{ tooltip: dataProduct.name }}
                                                    rootClassName={styles.title}
                                                >
                                                    {dataProduct.name}
                                                </Typography.Text>
                                            ),
                                        });
                                    }
                                }
                            }
                            if (datasetId && dataset && !isFetchingDataset) {
                                Object.assign(breadcrumbItem, {
                                    title: (
                                        <Typography.Text
                                            ellipsis={{ tooltip: dataset.name }}
                                            rootClassName={styles.title}
                                        >
                                            {dataset.name}
                                        </Typography.Text>
                                    ),
                                });
                            }

                            if (platformServiceConfigId && platformServiceConfig && !isFetchingPlatformServiceConfig) {
                                Object.assign(breadcrumbItem, {
                                    title: (
                                        <Space classNames={{ item: styles.breadcrumbItem }}>
                                            {`${platformServiceConfig.platform.name} - ${platformServiceConfig.service.name}`}
                                        </Space>
                                    ),
                                });
                            }

                            if (environmentId && environment && !isFetchingEnvironment) {
                                if (isEnvironmentConfigsPage(path, environmentId)) {
                                    break;
                                } else if (isEnvironmentConfigCreatePage(path, environmentId)) {
                                    Object.assign(breadcrumbItem, {
                                        title: (
                                            <Space
                                                classNames={{
                                                    item: styles.breadcrumbItem,
                                                }}
                                            >
                                                {t('New Environment Configuration')}
                                            </Space>
                                        ),
                                    });
                                } else {
                                    Object.assign(breadcrumbItem, {
                                        path: createEnvironmentConfigsPath(environmentId),
                                        title: (
                                            <Space
                                                classNames={{
                                                    item: styles.breadcrumbItem,
                                                }}
                                            >
                                                {environment.name}
                                            </Space>
                                        ),
                                    });
                                }
                            }

                            if (envConfigId && envConfig && !isFetchingEnvConfig) {
                                if (isEnvConfigPage(path, envConfigId)) {
                                    Object.assign(breadcrumbItem, {
                                        title: (
                                            <Space
                                                classNames={{
                                                    item: styles.breadcrumbItem,
                                                }}
                                            >
                                                {`${envConfig.platform.name}-${envConfig.service.name}`}
                                            </Space>
                                        ),
                                    });
                                } else {
                                    Object.assign(breadcrumbItem, {
                                        path: createEnvironmentConfigsPath(envConfig.environment.id),
                                        title: (
                                            <Space
                                                classNames={{
                                                    item: styles.breadcrumbItem,
                                                }}
                                            >
                                                {envConfig.environment.name}
                                            </Space>
                                        ),
                                    });
                                }
                            }

                            break;
                    }

                    if (breadcrumbItem.title === '') {
                        return null;
                    }

                    return breadcrumbItem;
                }),
            ].filter(Boolean) as Partial<BreadcrumbItemType & BreadcrumbSeparatorType>[],
        [
            pathnames,
            t,
            dataProductId,
            dataProduct,
            isFetchingDataProduct,
            datasetId,
            dataset,
            isFetchingDataset,
            platformServiceConfigId,
            platformServiceConfig,
            isFetchingPlatformServiceConfig,
            environmentId,
            environment,
            isFetchingEnvironment,
            envConfigId,
            envConfig,
            isFetchingEnvConfig,
            dataOutputId,
            dataOutput,
            isFetchingDataOutput,
        ],
    );

    return (
        <Breadcrumb
            itemRender={(route, _params, routes) => {
                const isLast = routes.indexOf(route) === routes.length - 1;
                return <BreadcrumbLink to={route.path} isActive={isLast} title={route.title} />;
            }}
            items={items}
            className={styles.breadcrumb}
            separator={
                <Space
                    classNames={{
                        item: styles.breadcrumbItem,
                    }}
                >
                    /
                </Space>
            }
        />
    );
};
