import Icon, { EditOutlined, LeftOutlined, ProductOutlined, RightOutlined } from '@ant-design/icons';
import { Flex, Space, Splitter, Typography } from 'antd';
import clsx from 'clsx';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataProductActions } from '@/pages/data-product/components/data-product-actions/data-product-actions.component.tsx';
import { DataProductDescription } from '@/pages/data-product/components/data-product-description/data-product-description.tsx';
import { DataProductTabs } from '@/pages/data-product/components/data-product-tabs/data-product-tabs.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetDataProductQuery,
    useGetDataProductRolledUpTagsQuery,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { useGetDataProductOwners } from '@/utils/data-product-user-role.helper.ts';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper.ts';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';
import styles from './data-product.module.scss';

export function DataProduct() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { dataProductId = '' } = useParams();
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined />
                        {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: <>{dataProduct?.name}</> },
        ]);
    }, [setBreadcrumbs, dataProduct, t]);
    const { data: { rolled_up_tags: rolledUpTags = [] } = {} } = useGetDataProductRolledUpTagsQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );

    const canEdit = edit_access?.allowed || false;

    const dataProductTypeIcon = useMemo(() => {
        return getDataProductTypeIcon(dataProduct?.type?.icon_key);
    }, [dataProduct?.type?.icon_key]);

    const dataProductOwners = useGetDataProductOwners(dataProduct?.id);

    function navigateToEditPage() {
        const destination = getDynamicRoutePath(
            ApplicationPaths.DataProductEdit,
            DynamicPathParams.DataProductId,
            dataProductId,
        );
        return navigate(destination);
    }

    useEffect(() => {
        setItemToLocalStorage(LocalStorageKeys.LastVisitedDataProducts, {
            id: dataProductId,
            timestamp: Date.now(),
        });
    }, [dataProductId]);

    //Only show the spinner when we have no data product to show, if we have one, we want to continue
    //Otherwise updating the settings for examples updates the whole page to a spinner, which is very weird
    if (isFetchingDataProduct && !dataProduct) return <LoadingSpinner />;

    if (!dataProduct) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    return (
        <Splitter className={styles.invisibleSplitter}>
            <Splitter.Panel size={sidebarCollapsed ? '100%' : '80%'} resizable={false} className={styles.container}>
                <Flex vertical gap={'middle'} className={styles.container}>
                    <Flex justify={'space-between'}>
                        <Flex gap={'middle'} align={'center'} justify={'center'}>
                            <Icon
                                component={dataProductTypeIcon}
                                className={clsx([styles.defaultIcon, styles.iconBorder])}
                            />
                            <Typography.Title
                                level={3}
                                ellipsis={{ tooltip: dataProduct?.name, rows: 2 }}
                                style={{ margin: 0 }}
                            >
                                {dataProduct?.name}
                            </Typography.Title>
                        </Flex>
                        <Space>
                            {canEdit && (
                                <CircleIconButton
                                    icon={<EditOutlined />}
                                    tooltip={t('Edit Data Product')}
                                    onClick={navigateToEditPage}
                                />
                            )}
                            <CircleIconButton
                                icon={sidebarCollapsed ? <LeftOutlined /> : <RightOutlined />}
                                tooltip={sidebarCollapsed ? t('Show sidebar') : t('Hide sidebar')}
                                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                            />
                        </Space>
                    </Flex>
                    <DataProductDescription
                        lifecycle={dataProduct.lifecycle}
                        type={dataProduct.type.name}
                        description={dataProduct.description}
                        domain={dataProduct.domain.name}
                        namespace={dataProduct.namespace}
                        tags={[...dataProduct.tags, ...rolledUpTags.map((tag) => ({ rolled_up: true, ...tag }))]}
                    />
                    <DataProductTabs dataProductId={dataProduct.id} />
                </Flex>
            </Splitter.Panel>
            <Splitter.Panel size={sidebarCollapsed ? '0%' : '20%'} resizable={false}>
                <Flex vertical className={styles.sidebarPanel}>
                    <DataProductActions dataProductId={dataProductId} />
                    <UserAccessOverview users={dataProductOwners} title={t('Data Product Owners')} />
                </Flex>
            </Splitter.Panel>
        </Splitter>
    );
}
