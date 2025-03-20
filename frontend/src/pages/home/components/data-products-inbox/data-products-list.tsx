import { Button, List } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { UsageListItem } from '@/components/list/usage-list-item/usage-list-item.component.tsx';
import styles from '@/pages/home/components/data-products-inbox/data-products-inbox.module.scss';
import { getLastVisitedItemDate } from '@/pages/home/helpers/last-visited-item-helper.ts';
import { DataProductsGetContract } from '@/types/data-product';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { formatDate } from '@/utils/date.helper.ts';
import { LastVisitedItem } from '@/utils/local-storage.helper.ts';

type DataProductListProps = {
    dataProducts?: DataProductsGetContract;
    isFetching: boolean;
    lastVisitedDataProducts: LastVisitedItem[];
};

export const DataProductsList = ({ dataProducts, isFetching, lastVisitedDataProducts }: DataProductListProps) => {
    const { t } = useTranslation();

    return (
        <List
            className={styles.cardList}
            dataSource={dataProducts}
            loading={isFetching}
            split
            loadMore={
                dataProducts?.length ? (
                    <Link to={ApplicationPaths.DataProducts}>
                        <Button type={'link'}>{t('Show More')}</Button>
                    </Link>
                ) : null
            }
            size={'small'}
            renderItem={(project) => {
                if (!project) return null;
                const lastVisitedDate = getLastVisitedItemDate(lastVisitedDataProducts, project.id);
                const formattedDate = lastVisitedDate ? formatDate(lastVisitedDate) : undefined;

                return (
                    <>
                        <UsageListItem
                            key={project.id}
                            itemId={project.id}
                            title={project.name}
                            description={
                                formattedDate
                                    ? t('Last opened on {{date}}', { date: formattedDate })
                                    : t('No recent activity')
                            }
                            icon={
                                <CustomSvgIconLoader
                                    iconComponent={getDataProductTypeIcon(project?.type?.icon_key)}
                                    hasRoundBorder
                                    size={'default'}
                                />
                            }
                            linkTo={createDataProductIdPath(project.id)}
                        />
                        <div />
                    </>
                );
            }}
        />
    );
};
