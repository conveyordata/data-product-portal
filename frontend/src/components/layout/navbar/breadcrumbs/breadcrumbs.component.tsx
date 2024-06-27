import { useLocation, useParams } from 'react-router-dom';
import { Breadcrumb, Space, Typography } from 'antd';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import Icon, { HomeOutlined, SettingOutlined, UnorderedListOutlined } from '@ant-design/icons';
import styles from './breadcrumbs.module.scss';
import { BreadcrumbItemType, BreadcrumbSeparatorType } from 'antd/es/breadcrumb/Breadcrumb';
import { useTranslation } from 'react-i18next';
import { BreadcrumbLink } from '@/components/layout/navbar/breadcrumbs/breadcrumb-link/breadcrumb-link.component.tsx';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ReactNode, useMemo } from 'react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import dataProductOutlineIcon from '@/assets/icons/data-product-outline-icon.svg?react';
import { isDataProductEditPage } from '@/utils/routes.helper.ts';

type BreadcrumbType = Partial<BreadcrumbItemType & BreadcrumbSeparatorType> & { icon?: ReactNode };

export const Breadcrumbs = () => {
    const { t } = useTranslation();
    const { pathname } = useLocation();
    const params = useParams<DynamicPathParams>();
    const pathnames =
        pathname === ApplicationPaths.Home ? [ApplicationPaths.Home] : pathname.split('/').filter((x) => x);
    const { dataProductId = '', datasetId = '' } = params;
    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductByIdQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { data: dataset, isFetching: isFetchingDataset } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });

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
                                        {t('Datasets')}
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
                        case ApplicationPaths.Settings:
                            Object.assign(breadcrumbItem, {
                                title: (
                                    <Space
                                        classNames={{
                                            item: styles.breadcrumbItem,
                                        }}
                                    >
                                        <SettingOutlined />
                                        {t('Settings')}
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
                                if (isDataProductEditPage(path, dataProductId)) {
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

                            break;
                    }

                    return breadcrumbItem;
                }),
            ].filter(Boolean) as Partial<BreadcrumbItemType & BreadcrumbSeparatorType>[],
        [pathnames, dataProductId, datasetId],
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
