import { Badge, Pagination, Typography } from 'antd';
import { TFunction } from 'i18next';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { useListPagination } from '@/hooks/use-list-pagination';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetDataOutputDatasetPendingActionsQuery } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import { useGetDataProductMembershipPendingActionsQuery } from '@/store/features/data-product-memberships/data-product-memberships-api-slice';
import { useGetDataProductDatasetPendingActionsQuery } from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { DataOutputDatasetContract } from '@/types/data-output-dataset';
import { DataProductDatasetContract } from '@/types/data-product-dataset';
import { DataProductMembershipContract } from '@/types/data-product-membership';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';

import styles from './pending-requests-inbox.module.scss';
import { PendingRequestsList } from './pending-requests-list';

type PendingAction =
    | ({ type: 'data_product' } & DataProductDatasetContract)
    | ({ type: 'data_output' } & DataOutputDatasetContract)
    | ({ type: 'team' } & DataProductMembershipContract);

const createPendingItem = (action: PendingAction, t: TFunction) => {
    let link, description, navigatePath, date, author;

    switch (action.type) {
        case 'data_product':
            link = createDataProductIdPath(action.data_product_id);
            description = (
                <Typography.Text>
                    {t('Made a request for read access to the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {action.dataset.name}
                    </Link>{' '}
                    {t('dataset, on behalf of the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {action.data_product.name}
                    </Link>{' '}
                    {t('data product.')}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataProduct);
            date = action.requested_on;
            author = action.requested_by.first_name + ' ' + action.requested_by.last_name;
            break;

        case 'data_output':
            link = createDataOutputIdPath(action.data_output_id, action.data_output.owner_id);
            description = (
                <Typography.Text>
                    {t('Made a request for a link to the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {action.dataset.name}
                    </Link>{' '}
                    {t('dataset, on behalf of the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {action.data_output.name}
                    </Link>{' '}
                    {t('data output.')}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataOutput);
            date = action.requested_on;
            author = action.requested_by.first_name + ' ' + action.requested_by.last_name;
            break;

        case 'team':
            link = createDataProductIdPath(action.data_product_id);
            description = (
                <Typography.Text>
                    {t('Made a request to join the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {action.data_product.name}
                    </Link>{' '}
                    {t('data product team.')}
                </Typography.Text>
            );
            navigatePath = createDataProductIdPath(action.data_product_id, DataProductTabKeys.Team);
            date = action.requested_on;
            author = action.user.first_name + ' ' + action.user.last_name;
            break;

        default:
            return null;
    }

    return {
        key: action.id,
        description: description,
        navigatePath: navigatePath,
        date: date,
        author: author,
    };
};

export function PendingRequestsInbox() {
    const { t } = useTranslation();

    const { data: pendingActionsDatasets, isFetching: isFetchingPendingActionsDatasets } =
        useGetDataProductDatasetPendingActionsQuery();
    const { data: pendingActionsDataOutputs, isFetching: isFetchingPendingActionsDataOutputs } =
        useGetDataOutputDatasetPendingActionsQuery();
    const { data: pendingActionsDataProducts, isFetching: isFetchingPendingActionsDataProducts } =
        useGetDataProductMembershipPendingActionsQuery();

    const isFetching =
        isFetchingPendingActionsDatasets || isFetchingPendingActionsDataOutputs || isFetchingPendingActionsDataProducts;

    const pendingItems = useMemo(() => {
        const datasets = pendingActionsDatasets?.map((action) =>
            createPendingItem({ ...action, type: 'data_product' }, t),
        );
        const dataOutputs = pendingActionsDataOutputs?.map((action) =>
            createPendingItem({ ...action, type: 'data_output' }, t),
        );
        const dataProducts = pendingActionsDataProducts?.map((action) =>
            createPendingItem({ ...action, type: 'team' }, t),
        );

        return [...(datasets ?? []), ...(dataOutputs ?? []), ...(dataProducts ?? [])]
            .filter((item) => item !== null)
            .sort((a, b) => {
                if (!a?.date || !b?.date) {
                    return 0;
                }
                return new Date(a.date).getTime() - new Date(b.date).getTime();
            });
    }, [pendingActionsDatasets, pendingActionsDataOutputs, pendingActionsDataProducts, t]);

    const { pagination, handlePaginationChange } = useListPagination({});

    const onPaginationChange = (current: number, pageSize: number) => {
        handlePaginationChange({ current, pageSize });
    };
    if (!pendingItems.length) {
        return null;
    }
    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>
                    {t('Pending Requests')}{' '}
                    <Badge count={pendingItems.length} color="gray" className={styles.requestsInfo} />
                </Typography.Title>
                <Pagination
                    current={pagination.current}
                    pageSize={pagination.pageSize}
                    total={pendingItems.length}
                    onChange={onPaginationChange}
                    size="small"
                />
            </div>
            <div className={styles.requestsListContainer}>
                <PendingRequestsList
                    pendingActionItems={pendingItems}
                    isFetching={isFetching}
                    pagination={pagination}
                />
            </div>
        </div>
    );
}
