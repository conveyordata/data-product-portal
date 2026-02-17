import {
    CompassOutlined,
    HomeOutlined,
    ProductOutlined,
    ShopOutlined,
    ShoppingCartOutlined,
    TeamOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import { Breadcrumb, Space, Typography } from 'antd';
import type { BreadcrumbItemType, BreadcrumbSeparatorType } from 'antd/es/breadcrumb/Breadcrumb';
import { type ReactNode, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router';
import { BreadcrumbLink } from '@/components/layout/navbar/breadcrumbs/breadcrumb-link/breadcrumb-link.component.tsx';
import { TabKeys as DataOutputTabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths, type DynamicPathParams } from '@/types/navigation.ts';
import { isDataOutputEditPage, isDataProductEditPage, isDatasetEditPage } from '@/utils/routes.helper.ts';
import styles from './breadcrumbs.module.scss';

type BreadcrumbType = Partial<BreadcrumbItemType & BreadcrumbSeparatorType> & { icon?: ReactNode };

export const Breadcrumbs = () => {
    const { t } = useTranslation();
    const { pathname } = useLocation();
    const params = useParams<DynamicPathParams>();
    const pathnames = useMemo(
        () =>
            pathname === ApplicationPaths.Home
                ? [ApplicationPaths.Home]
                : pathname.split('/').filter((x) => x && x !== 'output-port'),
        [pathname],
    );
    const { dataProductId = '', datasetId = '', dataOutputId = '' } = params;
    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductByIdQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { data: dataOutput, isFetching: isFetchingDataOutput } = useGetDataOutputByIdQuery(dataOutputId, {
        skip: !dataOutputId,
    });
    const { data: dataset, isFetching: isFetchingDataset } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });

    const homeItem: BreadcrumbItemType = useMemo(
        () => ({
            path: ApplicationPaths.Home,
            title: (
                <Space>
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
                case ApplicationPaths.Studio:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space>
                                <ProductOutlined />
                                {t('Product Studio')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.DataProductNew:
                    Object.assign(breadcrumbItem, {
                        title: t('New Data Product'),
                    });
                    break;
                case ApplicationPaths.Datasets:
                case ApplicationPaths.Marketplace:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space>
                                <ShopOutlined />
                                {t('Marketplace')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.MarketplaceCart:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space>
                                <ShoppingCartOutlined />
                                {t('Cart')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.AuditLogs:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space>
                                <UnorderedListOutlined />
                                {t('Audit Logs')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.Explorer:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space>
                                <CompassOutlined />
                                {t('Explorer')}
                            </Space>
                        ),
                    });
                    break;
                case ApplicationPaths.Settings:
                    Object.assign(breadcrumbItem, {
                        title: t('Settings'),
                    });
                    break;
                case ApplicationPaths.People:
                    Object.assign(breadcrumbItem, {
                        title: (
                            <Space>
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
                    // Case for Data Product and Output Port
                    if (
                        dataProduct &&
                        !isFetchingDataProduct &&
                        pathnames.includes(ApplicationPaths.Studio.replace('/', ''))
                    ) {
                        if (
                            isDataProductEditPage(path, dataProduct.id) ||
                            (dataOutput && isDataOutputEditPage(path, dataOutput.id, dataProduct.id)) ||
                            (dataset && isDatasetEditPage(path, dataset.id))
                        ) {
                            Object.assign(breadcrumbItem, {
                                title: t('Edit'),
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
                                if (dataset && !isFetchingDataset && path.split('/').length === 4) {
                                    Object.assign(breadcrumbItem, {
                                        path: `${path}#${DatasetTabKeys.About}`,
                                        title: (
                                            <Typography.Text
                                                ellipsis={{ tooltip: dataset.name }}
                                                rootClassName={styles.title}
                                            >
                                                {dataset.name}
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
                    }
                    if (
                        dataset &&
                        !isFetchingDataset &&
                        pathnames.includes(ApplicationPaths.Datasets.replace('/', ''))
                    ) {
                        if (isDatasetEditPage(path, dataset.id)) {
                            Object.assign(breadcrumbItem, {
                                title: t('Edit'),
                            });
                        } else {
                            Object.assign(breadcrumbItem, {
                                path: `${path}#${DatasetTabKeys.About}`,
                                title: (
                                    <Typography.Text ellipsis={{ tooltip: dataset.name }} rootClassName={styles.title}>
                                        {dataset.name}
                                    </Typography.Text>
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
            pathnames,
            isFetchingDataset,
            isFetchingDataProduct,
            isFetchingDataOutput,
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
                    <Space>
                        <HomeOutlined />
                    </Space>
                ),
            },
            ...pathnames.map((pathname, index) => renderBreadcrumbItem(pathname, index)),
        ].filter(Boolean) as Partial<BreadcrumbItemType & BreadcrumbSeparatorType>[];
    }, [renderBreadcrumbItem, pathnames, homeItem]);

    return (
        <Breadcrumb
            className={styles.breadcrumb}
            itemRender={(route, _params, routes) => {
                const isLast = routes.indexOf(route) === routes.length - 1;
                return <BreadcrumbLink to={route.path} isActive={isLast} title={route.title} />;
            }}
            items={items}
            separator={'/'}
        />
    );
};
