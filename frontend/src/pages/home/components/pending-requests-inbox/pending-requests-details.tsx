import { PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { Button, Tabs, Typography } from 'antd';
import { ReactNode, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DatasetList } from '@/pages/home/components/datasets-inbox/datasets-list.tsx';
import { filterOutNonMatchingItems, sortLastVisitedOwnedItems } from '@/pages/home/helpers/last-visited-item-helper.ts';
import { useGetAllDatasetsQuery, useGetUserDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { getItemFromLocalStorage, LastVisitedItem, LocalStorageKeys } from '@/utils/local-storage.helper.ts';

import styles from './pending-requests-inbox.module.scss';

type Props = {
    userId: string;
};

enum InboxTabKeys {
    LastViewed = 'last-viewed',
    Owned = 'owned',
}

type DatasetInboxTab = {
    label: string;
    key: InboxTabKeys;
    icon?: ReactNode;
    children: ReactNode;
    linkTo?: string;
};

export function PendingRequestsDetails({ userId }: Props) {
    const { t } = useTranslation();
    const { data: datasets, isFetching } = useGetAllDatasetsQuery();
    const { data: userDatasets, isFetching: isFetchingOwnedDatasets } = useGetUserDatasetsQuery(userId);
    const [lastVisitedDatasets, setLastVisitedDatasets] = useState<LastVisitedItem[]>([]);

    const filteredLastVisitedDatasets = useMemo(
        () => filterOutNonMatchingItems(lastVisitedDatasets, datasets)?.slice(0, 4),
        [datasets, lastVisitedDatasets],
    );
    const sortedOwnedDatasets = useMemo(
        () => sortLastVisitedOwnedItems(lastVisitedDatasets, userDatasets)?.slice(0, 4),
        [userDatasets, lastVisitedDatasets],
    );

    const lastViewed: DatasetInboxTab = useMemo(
        () => ({
            label: t('Customer Data Dataset'),
            key: InboxTabKeys.LastViewed,
            icon: <PartitionOutlined />,
            children: <Typography.Text>{t('INFO')}</Typography.Text>,
        }),
        [filteredLastVisitedDatasets, isFetching, lastVisitedDatasets, t],
    );

    const owned: DatasetInboxTab = useMemo(
        () => ({
            label: t('Customer Analysis Data Product'),
            key: InboxTabKeys.Owned,
            children: <Typography.Text>{t('INFO')}</Typography.Text>,
            icon: <TeamOutlined />,
        }),
        [isFetchingOwnedDatasets, lastVisitedDatasets, sortedOwnedDatasets, t],
    );

    const items: DatasetInboxTab[] = useMemo(() => [lastViewed, owned], [lastViewed, owned]);

    useEffect(() => {
        setLastVisitedDatasets(getItemFromLocalStorage(LocalStorageKeys.LastVisitedDatasets));
    }, []);

    if (isFetching) return <LoadingSpinner />;

    return <div className={styles.section}></div>;
}
