import { PartitionOutlined, TeamOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Button, Tabs, Typography } from 'antd';
import { type ReactNode, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { PosthogEvents } from '@/constants/posthog.constants';
import { DatasetList } from '@/pages/home/components/datasets-inbox/datasets-list.tsx';
import { filterOutNonMatchingItems, sortLastVisitedOwnedItems } from '@/pages/home/helpers/last-visited-item-helper.ts';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { getItemFromLocalStorage, type LastVisitedItem, LocalStorageKeys } from '@/utils/local-storage.helper.ts';
import styles from './datasets-inbox.module.scss';

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

export function DatasetsInbox() {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const [activeTab, setActiveTab] = useState<InboxTabKeys>();
    const { data: { output_ports: outputPorts = [] } = {}, isFetching } = useSearchOutputPortsQuery({
        currentUserAssigned: activeTab === InboxTabKeys.Owned,
        limit: 1000,
    });

    const lastVisitedOutputPorts: LastVisitedItem[] = getItemFromLocalStorage(LocalStorageKeys.LastVisitedDatasets);
    const filteredDatasets = useMemo(() => {
        if (activeTab === InboxTabKeys.Owned) {
            return sortLastVisitedOwnedItems(lastVisitedOutputPorts, outputPorts)?.slice(0, 4);
        }
        return filterOutNonMatchingItems(lastVisitedOutputPorts, outputPorts)?.slice(0, 4);
    }, [activeTab, outputPorts, lastVisitedOutputPorts]);

    const lastViewed: DatasetInboxTab = useMemo(
        () => ({
            label: t('Last Viewed'),
            key: InboxTabKeys.LastViewed,
            icon: <PartitionOutlined />,
            children: (
                <DatasetList
                    datasets={filteredDatasets}
                    isFetching={isFetching}
                    lastVisitedDatasets={lastVisitedOutputPorts}
                />
            ),
        }),
        [filteredDatasets, isFetching, lastVisitedOutputPorts, t],
    );

    const owned: DatasetInboxTab = useMemo(
        () => ({
            label: t('Your Output Ports'),
            key: InboxTabKeys.Owned,
            children: (
                <DatasetList
                    datasets={filteredDatasets}
                    isFetching={isFetching}
                    lastVisitedDatasets={lastVisitedOutputPorts}
                />
            ),
            icon: <TeamOutlined />,
        }),
        [isFetching, lastVisitedOutputPorts, t, filteredDatasets],
    );

    const items: DatasetInboxTab[] = useMemo(() => [lastViewed, owned], [lastViewed, owned]);

    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>{t('Output Ports')}</Typography.Title>
                <Link to={ApplicationPaths.Marketplace}>
                    <Button className={styles.formButton}>{t('See All')}</Button>
                </Link>
            </div>
            <Tabs
                defaultActiveKey={InboxTabKeys.LastViewed}
                items={items}
                activeKey={activeTab}
                onTabClick={(activeKey) => setActiveTab(activeKey as InboxTabKeys)}
                onChange={(activeKey) =>
                    posthog.capture(PosthogEvents.HOMEPAGE_DATASETS_TAB_CLICKED, { tab_name: activeKey })
                }
            />
        </div>
    );
}
