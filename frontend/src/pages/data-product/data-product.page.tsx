import Icon, { EditOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import clsx from 'clsx';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataProductActions } from '@/pages/data-product/components/data-product-actions/data-product-actions.component.tsx';
import { DataProductDescription } from '@/pages/data-product/components/data-product-description/data-product-description.tsx';
import { DataProductTabs } from '@/pages/data-product/components/data-product-tabs/data-product-tabs.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
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

    const { data: dataProduct, isLoading } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });
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

    if (isLoading) return <LoadingSpinner />;

    if (!dataProduct) {
        navigate(ApplicationPaths.DataProducts, { replace: true });
        return null;
    }

    return (
        <Flex className={styles.dataProductContainer}>
            <Flex vertical className={clsx(styles.content, { [styles.contentExpanded]: sidebarCollapsed })}>
                <Flex className={styles.headerContainer}>
                    <Space className={styles.header}>
                        <Icon
                            component={dataProductTypeIcon}
                            className={clsx([styles.defaultIcon, styles.iconBorder])}
                        />
                        <Typography.Title level={3} ellipsis={{ tooltip: dataProduct?.name, rows: 2 }}>
                            {dataProduct?.name}
                        </Typography.Title>
                    </Space>
                    <Space className={styles.editIcon}>
                        {canEdit && (
                            <CircleIconButton
                                icon={<EditOutlined />}
                                tooltip={t('Edit data product')}
                                onClick={navigateToEditPage}
                            />
                        )}
                        {!sidebarCollapsed && (
                            <CircleIconButton
                                icon={<RightOutlined />}
                                tooltip={t('Hide sidebar')}
                                onClick={() => setSidebarCollapsed(true)}
                            />
                        )}
                    </Space>
                </Flex>
                {/* Main content */}
                <Flex className={styles.mainContent}>
                    {/* Data product description */}
                    <Flex vertical className={styles.overview}>
                        <DataProductDescription
                            lifecycle={dataProduct.lifecycle}
                            type={dataProduct.type.name}
                            description={dataProduct.description}
                            domain={dataProduct.domain.name}
                            namespace={dataProduct.namespace}
                            tags={[
                                ...dataProduct.tags,
                                ...dataProduct.rolled_up_tags.map((tag) => ({ rolled_up: true, ...tag })),
                            ]}
                        />
                        {/*  Tabs  */}
                        <DataProductTabs dataProductId={dataProduct.id} isLoading={isLoading} />
                    </Flex>
                </Flex>
            </Flex>

            {/* Sidebar */}
            <Flex vertical className={clsx(styles.sidebar, { [styles.sidebarCollapsed]: sidebarCollapsed })}>
                {!sidebarCollapsed ? (
                    <>
                        <DataProductActions dataProductId={dataProductId} />
                        <UserAccessOverview users={dataProductOwners} title={t('Data Product Owners')} />
                    </>
                ) : (
                    <Flex vertical className={styles.collapsedSidebar}>
                        <div className={styles.spacer} />
                        <Flex className={styles.expandButton}>
                            <CircleIconButton
                                icon={<LeftOutlined />}
                                tooltip={t('Show sidebar')}
                                onClick={() => setSidebarCollapsed(false)}
                            />
                        </Flex>
                        <UserAccessOverview users={dataProductOwners} title="" showAvatarsOnly={true} />
                    </Flex>
                )}
            </Flex>
        </Flex>
    );
}
