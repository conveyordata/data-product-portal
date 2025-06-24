import {
    CompassOutlined,
    HomeOutlined,
    SettingOutlined,
    ShopOutlined,
    TeamOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import { Breadcrumb, Space, Typography } from 'antd';
import type { BreadcrumbItemType, BreadcrumbSeparatorType } from 'antd/es/breadcrumb/Breadcrumb';
import { type ReactNode, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { BreadcrumbLink } from '@/components/layout/navbar/breadcrumbs/breadcrumb-link/breadcrumb-link.component.tsx';
import { TabKeys as DataOutputTabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import {
    useGetEnvConfigByIdQuery,
    useGetEnvironmentByIdQuery,
} from '@/store/features/environments/environments-api-slice';
import { useGetPlatformServiceConfigByIdQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { ApplicationPaths, createEnvironmentConfigsPath, type DynamicPathParams } from '@/types/navigation.ts';
import {
    isDataOutputEditPage,
    isDataProductEditPage,
    isDatasetEditPage,
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

    const homeItem: BreadcrumbItemType = useMemo(
        () => ({
            path: ApplicationPaths.Home,
            title: (
                <Space classNames={{ item: styles.breadcrumbItem }}>
                    <HomeOutlined />
                    {t('Home')}
                </Space>
            ),
        }),
        [t],
    );

    const renderBreadcrumbItem = useCallback(
        (pathname: string, index: number) => {
            const path = `/${pathnames.slice(0, index + 1).join('/')}`;
            const breadcrumbItem: Partial<BreadcrumbItemType> = {
                path,
                title: pathname,
            };

            switch (path) {
                case ApplicationPaths.DataProducts:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space classNames={{ item: styles.breadcrumbItem }}>
                                <DataProductOutlined />
                                {t('Data Products')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.DataProductNew:
                    Object.assign(breadcrumbItem, {
                        title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('New Data Product')}</Space>,
                    });
                    break;
                case ApplicationPaths.Datasets:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space classNames={{ item: styles.breadcrumbItem }}>
                                <ShopOutlined />
                                {t('Marketplace')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.DatasetNew:
                    Object.assign(breadcrumbItem, {
                        title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('New Dataset')}</Space>,
                    });
                    break;
                case ApplicationPaths.AuditLogs:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space classNames={{ item: styles.breadcrumbItem }}>
                                <UnorderedListOutlined />
                                {t('Audit Logs')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.Explorer:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space classNames={{ item: styles.breadcrumbItem }}>
                                <CompassOutlined />
                                {t('Explorer')}
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
                        title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('New Environment')}</Space>,
                    });
                    break;
                case ApplicationPaths.Settings:
                    Object.assign(breadcrumbItem, {
                        title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('Settings')}</Space>,
                    });
                    break;
                case ApplicationPaths.PlatformServiceConfigNew:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space classNames={{ item: styles.breadcrumbItem }}>
                                {t('New Platform Service Configuration')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.RoleConfiguration:
                    Object.assign(breadcrumbItem, {
                        title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('Role Management')}</Space>,
                    });
                    break;
                case ApplicationPaths.People:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space classNames={{ item: styles.breadcrumbItem }}>
                                <TeamOutlined />
                                {t('People')}
                            </Space>
                        ),
                    });
                    break;
                default:
                    Object.assign(breadcrumbItem, {
                        title: '',
                    });

                    // Case for data product and dataset
                    if (
                        dataProduct &&
                        !isFetchingDataProduct &&
                        pathnames.includes(ApplicationPaths.DataProducts.replace('/', ''))
                    ) {
                        if (
                            isDataProductEditPage(path, dataProduct.id) ||
                            (dataOutput && isDataOutputEditPage(path, dataOutput.id, dataProduct.id))
                        ) {
                            Object.assign(breadcrumbItem, {
                                title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('Edit')}</Space>,
                            });
                        } else {
                            if (dataOutput && !isFetchingDataOutput && path.split('/').length === 4) {
                                Object.assign(breadcrumbItem, {
                                    path: `${path}#${DataOutputTabKeys.Datasets}`,
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
                                    path: `${path}#${DataProductTabKeys.About}`,
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
                    if (
                        dataset &&
                        !isFetchingDataset &&
                        pathnames.includes(ApplicationPaths.Datasets.replace('/', ''))
                    ) {
                        if (isDatasetEditPage(path, dataset.id)) {
                            Object.assign(breadcrumbItem, {
                                title: <Space classNames={{ item: styles.breadcrumbItem }}>{t('Edit')}</Space>,
                            });
                        } else {
                            Object.assign(breadcrumbItem, {
                                path: `${path}#${DatasetTabKeys.About}`,
                                title: (
                                    <Space>
                                        <DatasetOutlined />
                                        <Typography.Text
                                            ellipsis={{ tooltip: dataset.name }}
                                            rootClassName={styles.title}
                                        >
                                            {dataset.name}
                                        </Typography.Text>
                                    </Space>
                                ),
                            });
                        }
                    }

                    if (platformServiceConfig && !isFetchingPlatformServiceConfig) {
                        Object.assign(breadcrumbItem, {
                            title: (
                                <Space classNames={{ item: styles.breadcrumbItem }}>
                                    {`${platformServiceConfig.platform.name} - ${platformServiceConfig.service.name}`}
                                </Space>
                            ),
                        });
                    }

                    if (environment && !isFetchingEnvironment) {
                        if (isEnvironmentConfigsPage(path, environment.id)) {
                            break;
                        }
                        if (isEnvironmentConfigCreatePage(path, environment.id)) {
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space classNames={{ item: styles.breadcrumbItem }}>
                                        {t('New Environment Configuration')}
                                    </Space>
                                ),
                            });
                        } else {
                            Object.assign(breadcrumbItem, {
                                path: createEnvironmentConfigsPath(environment.id),
                                title: <Space classNames={{ item: styles.breadcrumbItem }}>{environment.name}</Space>,
                            });
                        }
                    }

                    if (envConfig && !isFetchingEnvConfig) {
                        if (isEnvConfigPage(path, envConfig.id)) {
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space classNames={{ item: styles.breadcrumbItem }}>
                                        {`${envConfig.platform.name}-${envConfig.service.name}`}
                                    </Space>
                                ),
                            });
                        } else {
                            Object.assign(breadcrumbItem, {
                                path: createEnvironmentConfigsPath(envConfig.environment.id),
                                title: (
                                    <Space classNames={{ item: styles.breadcrumbItem }}>
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
        },
        [
            t,
            dataset,
            dataProduct,
            dataOutput,
            envConfig,
            environment,
            pathnames,
            platformServiceConfig,
            isFetchingDataset,
            isFetchingDataProduct,
            isFetchingDataOutput,
            isFetchingEnvConfig,
            isFetchingEnvironment,
            isFetchingPlatformServiceConfig,
        ],
    );

    const items: BreadcrumbType[] = useMemo(() => {
        if (pathnames[0] === ApplicationPaths.Home) {
            return [homeItem];
        }

        return [
            {
                path: ApplicationPaths.Home,
                title: (
                    <Space classNames={{ item: styles.breadcrumbItem }}>
                        <HomeOutlined />
                    </Space>
                ),
            },
            ...pathnames.map((pathname, index) => renderBreadcrumbItem(pathname, index)),
        ].filter(Boolean) as Partial<BreadcrumbItemType & BreadcrumbSeparatorType>[];
    }, [renderBreadcrumbItem, pathnames, homeItem]);

    return (
        <Breadcrumb
            itemRender={(route, _params, routes) => {
                const isLast = routes.indexOf(route) === routes.length - 1;
                return <BreadcrumbLink to={route.path} isActive={isLast} title={route.title} />;
            }}
            items={items}
            className={styles.breadcrumb}
            separator={<Space classNames={{ item: styles.breadcrumbItem }}>/</Space>}
        />
    );
};
