import { PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { Button, Tabs, Typography } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { filterOutNonMatchingItems, sortLastVisitedOwnedItems } from '@/pages/home/helpers/last-visited-item-helper.ts';
import {
    useGetAllDataProductsQuery,
    useGetUserDataProductsQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
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
    const { data: dataProducts, isFetching } = useGetAllDataProductsQuery();
    const { data: userDataProducts, isFetching: isFetchingUserDataProducts } = useGetUserDataProductsQuery(userId);

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
                    isFetching={isFetching}
                    lastVisitedDataProducts={lastVisitedDataProducts}
                />
            ),
        }),
        [t, filteredLastVisitedDataProducts, isFetching, lastVisitedDataProducts],
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

    if (isFetching) return <LoadingSpinner />;
    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>{t('Data Products')}</Typography.Title>
                <Link to={ApplicationPaths.DataProducts}>
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
