import Icon, { SettingOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import clsx from 'clsx';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router';

import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataProductActions } from '@/pages/data-product/components/data-product-actions/data-product-actions.component.tsx';
import { DataProductDescription } from '@/pages/data-product/components/data-product-description/data-product-description.tsx';
import { DataProductTabs } from '@/pages/data-product/components/data-product-tabs/data-product-tabs.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { getDataProductOwners, getIsDataProductOwner } from '@/utils/data-product-user-role.helper.ts';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper.ts';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';

import styles from './data-product.module.scss';

export function DataProduct() {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const { dataProductId = '' } = useParams();
    const { data: dataProduct, isLoading } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });
    const navigate = useNavigate();
    const { data: edit_access } = useCheckAccessQuery(
        {
            object_id: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );

    const canEditProduct = edit_access?.access || false;

    const dataProductTypeIcon = useMemo(() => {
        return getDataProductTypeIcon(dataProduct?.type?.icon_key);
    }, [dataProduct?.type?.icon_key]);

    const dataProductOwners = dataProduct ? getDataProductOwners(dataProduct) : [];

    const isCurrentDataProductOwner = Boolean(
        dataProduct && currentUser && (getIsDataProductOwner(dataProduct, currentUser?.id) || currentUser?.is_admin),
    );

    function navigateToEditPage() {
        if (canEditProduct || (isCurrentDataProductOwner && dataProductId)) {
            navigate(
                getDynamicRoutePath(ApplicationPaths.DataProductEdit, DynamicPathParams.DataProductId, dataProductId),
            );
        }
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
            <Flex vertical className={styles.content}>
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
                    {(canEditProduct || isCurrentDataProductOwner) && (
                        <Space className={styles.editIcon}>
                            <CircleIconButton
                                icon={<SettingOutlined />}
                                tooltip={t('Edit data product')}
                                onClick={navigateToEditPage}
                            />
                        </Space>
                    )}
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
            <Flex vertical className={styles.sidebar}>
                <DataProductActions dataProductId={dataProductId} />
                {/*  Data product owners overview */}
                <UserAccessOverview users={dataProductOwners} title={t('Data Product Owners')} />
            </Flex>
        </Flex>
    );
}
