import { Button, List } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { UsageListItem } from '@/components/list/usage-list-item/usage-list-item.component.tsx';
import styles from '@/pages/home/components/datasets-inbox/datasets-inbox.module.scss';
import { getLastVisitedItemDate } from '@/pages/home/helpers/last-visited-item-helper.ts';
import { DatasetsGetContract } from '@/types/dataset';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
import { formatDate } from '@/utils/date.helper.ts';
import { LastVisitedItem } from '@/utils/local-storage.helper.ts';

type DatasetListProps = {
    datasets?: DatasetsGetContract;
    isFetching: boolean;
    lastVisitedDatasets: LastVisitedItem[];
};

export const DatasetList = ({ datasets, isFetching, lastVisitedDatasets }: DatasetListProps) => {
    const { t } = useTranslation();

    return (
        <List
            className={styles.cardList}
            dataSource={datasets}
            loading={isFetching}
            split
            loadMore={
                datasets?.length ? (
                    <Link to={ApplicationPaths.Datasets}>
                        <Button type={'link'}>{t('Show More')}</Button>
                    </Link>
                ) : null
            }
            size={'small'}
            renderItem={(dataset) => {
                if (!dataset) return null;
                const lastVisitedDate = getLastVisitedItemDate(lastVisitedDatasets, dataset.id);
                const formattedDate = lastVisitedDate ? formatDate(lastVisitedDate) : undefined;

                return (
                    <>
                        <UsageListItem
                            key={dataset.id}
                            itemId={dataset.id}
                            title={dataset.name}
                            description={
                                formattedDate
                                    ? t('Last opened on {{date}}', { date: formattedDate })
                                    : t('No recent activity')
                            }
                            icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                            linkTo={createDatasetIdPath(dataset.id)}
                        />
                        <div />
                    </>
                );
            }}
        />
    );
};
