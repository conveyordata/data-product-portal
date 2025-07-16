import { PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { Button, Tabs, Typography } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { DatasetList } from '@/pages/home/components/datasets-inbox/datasets-list.tsx';
import { filterOutNonMatchingItems, sortLastVisitedOwnedItems } from '@/pages/home/helpers/last-visited-item-helper.ts';
import { useGetAllDatasetsQuery, useGetUserDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { getItemFromLocalStorage, type LastVisitedItem, LocalStorageKeys } from '@/utils/local-storage.helper.ts';
import styles from './datasets-inbox.module.scss';

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

export function DatasetsInbox({ userId }: Props) {
    const { t } = useTranslation();
    const { data: datasets, isFetching } = useGetAllDatasetsQuery();
    const { data: userDatasets, isFetching: isFetchingOwnedDatasets } = useGetUserDatasetsQuery(userId);

    const lastVisitedDatasets: LastVisitedItem[] = getItemFromLocalStorage(LocalStorageKeys.LastVisitedDatasets);
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
            label: t('Last Viewed'),
            key: InboxTabKeys.LastViewed,
            icon: <PartitionOutlined />,
            children: (
                <DatasetList
                    datasets={filteredLastVisitedDatasets}
                    isFetching={isFetching}
                    lastVisitedDatasets={lastVisitedDatasets}
                />
            ),
        }),
        [filteredLastVisitedDatasets, isFetching, lastVisitedDatasets, t],
    );

    const owned: DatasetInboxTab = useMemo(
        () => ({
            label: t('Your Datasets'),
            key: InboxTabKeys.Owned,
            children: (
                <DatasetList
                    datasets={sortedOwnedDatasets}
                    isFetching={isFetchingOwnedDatasets}
                    lastVisitedDatasets={lastVisitedDatasets}
                />
            ),
            icon: <TeamOutlined />,
        }),
        [isFetchingOwnedDatasets, lastVisitedDatasets, sortedOwnedDatasets, t],
    );

    const items: DatasetInboxTab[] = useMemo(() => [lastViewed, owned], [lastViewed, owned]);

    if (isFetching) return <LoadingSpinner />;

    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>{t('Datasets')}</Typography.Title>
                <Link to={ApplicationPaths.Datasets}>
                    <Button className={styles.formButton}>{t('See All')}</Button>
                </Link>
            </div>
            <Tabs
                defaultActiveKey={InboxTabKeys.LastViewed}
                items={items}
                onChange={(activeKey) =>
                    posthog.capture(PosthogEvents.HOMEPAGE_DATASETS_TAB_CLICKED, { tab_name: activeKey })
                }
            />
        </div>
    );
}
