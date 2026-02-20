import { PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Button, Tabs, Typography } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { filterOutNonMatchingItems, sortLastVisitedOwnedItems } from '@/pages/home/helpers/last-visited-item-helper.ts';
import { useGetDataProductsQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { getItemFromLocalStorage, type LastVisitedItem, LocalStorageKeys } from '@/utils/local-storage.helper.ts';
import styles from './data-products-inbox.module.scss';
import { DataProductsList } from './data-products-list.tsx';

type Props = {
    userId: string;
};

enum InboxTabKeys {
    LastViewed = 'last-viewed',
    Owned = 'owned',
}

type InboxTab = {
    label: string;
    key: InboxTabKeys;
    icon?: ReactNode;
    children: ReactNode;
};

export function DataProductsInbox({ userId }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const { data: { data_products: userDataProducts = [] } = {}, isFetching: isFetchingUserDataProducts } =
        useGetDataProductsQuery(userId);

    const { data: { data_products: dataProducts = [] } = {}, isFetching: isFetchingAll } =
        useGetDataProductsQuery(undefined);

    const lastVisitedDataProducts: LastVisitedItem[] = getItemFromLocalStorage(
        LocalStorageKeys.LastVisitedDataProducts,
    );
    const filteredLastVisitedDataProducts = useMemo(() => {
        return filterOutNonMatchingItems(lastVisitedDataProducts, dataProducts)?.slice(0, 4);
    }, [dataProducts, lastVisitedDataProducts]);
    const sortedUserDataProducts = useMemo(
        () => sortLastVisitedOwnedItems(lastVisitedDataProducts, userDataProducts)?.slice(0, 4),
        [userDataProducts, lastVisitedDataProducts],
    );

    const lastViewed: InboxTab = useMemo(
        () => ({
            label: t('Last Viewed'),
            key: InboxTabKeys.LastViewed,
            icon: <PartitionOutlined />,
            children: (
                <DataProductsList
                    dataProducts={filteredLastVisitedDataProducts}
                    isFetching={isFetchingAll}
                    lastVisitedDataProducts={lastVisitedDataProducts}
                />
            ),
        }),
        [t, filteredLastVisitedDataProducts, isFetchingAll, lastVisitedDataProducts],
    );

    const owned: InboxTab = useMemo(
        () => ({
            label: t('Your Data Products'),
            key: InboxTabKeys.Owned,
            children: (
                <DataProductsList
                    dataProducts={sortedUserDataProducts}
                    isFetching={isFetchingUserDataProducts}
                    lastVisitedDataProducts={lastVisitedDataProducts}
                />
            ),
            icon: <TeamOutlined />,
        }),
        [t, sortedUserDataProducts, isFetchingUserDataProducts, lastVisitedDataProducts],
    );

    const items: InboxTab[] = useMemo(() => [lastViewed, owned], [lastViewed, owned]);

    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>{t('Data Products')}</Typography.Title>
                <Link to={`${ApplicationPaths.Studio}#data-products`}>
                    <Button className={styles.formButton}>{t('See All')}</Button>
                </Link>
            </div>
            <Tabs
                defaultActiveKey={InboxTabKeys.LastViewed}
                items={items}
                onChange={(activeKey) =>
                    posthog.capture(PosthogEvents.HOMEPAGE_DATA_PRODUCTS_TAB_CLICKED, { tab_name: activeKey })
                }
            />
        </div>
    );
}
