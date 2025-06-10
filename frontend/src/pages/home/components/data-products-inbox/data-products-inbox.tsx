import { PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { Button, Tabs, Typography } from 'antd';
import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { filterOutNonMatchingItems, sortLastVisitedOwnedItems } from '@/pages/home/helpers/last-visited-item-helper.ts';
import {
    useGetAllDataProductsQuery,
    useGetUserDataProductsQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { type LastVisitedItem, LocalStorageKeys, getItemFromLocalStorage } from '@/utils/local-storage.helper.ts';

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
    const [lastVisitedDataProducts, setLastVisitedDataProducts] = useState<LastVisitedItem[]>([]);

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

    useEffect(() => {
        setLastVisitedDataProducts(getItemFromLocalStorage(LocalStorageKeys.LastVisitedDataProducts));
    }, []);

    if (isFetching) return <LoadingSpinner />;
    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>{t('Data Products')}</Typography.Title>
                <Link to={ApplicationPaths.DataProducts}>
                    <Button className={styles.formButton}>{t('See All')}</Button>
                </Link>
            </div>
            <Tabs defaultActiveKey={InboxTabKeys.LastViewed} items={items} />
        </div>
    );
}
