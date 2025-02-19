import { Pagination, Typography } from 'antd';
import styles from './pending-requests-inbox.module.scss';
import { useTranslation } from 'react-i18next';
import { useGetDataProductDatasetPendingActionsQuery } from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { useGetDataOutputDatasetPendingActionsQuery } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import { useGetDataProductMembershipPendingActionsQuery } from '@/store/features/data-product-memberships/data-product-memberships-api-slice';
import { PendingRequestsList } from './pending-requests-list';
import { useMemo, useState } from 'react';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabs';
import { DataOutputDatasetContract } from '@/types/data-output-dataset';
import { DataProductDatasetContract } from '@/types/data-product-dataset';
import { DataProductMembershipContract } from '@/types/data-product-membership';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabs';
import { TFunction } from 'i18next';
import { Link } from 'react-router-dom';

const PAGE_SIZE = 3;

type PendingAction =
    | ({ type: 'data_product' } & DataProductDatasetContract)
    | ({ type: 'data_output' } & DataOutputDatasetContract)
    | ({ type: 'team' } & DataProductMembershipContract);

const createPendingItem = (action: PendingAction, t: TFunction) => {
    let link, description, navigatePath, date;

    switch (action.type) {
        case 'data_product':
            link = createDataProductIdPath(action.data_product_id);
            description = (
                <>
                    <Typography.Text style={{ marginRight: '4px' }}>
                        {t('{{name}}, on behalf of data product', { name: action.requested_by?.first_name })}
                    </Typography.Text>
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {t('{{name}}', { name: action.data_product.name })}
                    </Link>
                    <Typography.Text style={{ marginRight: '4px', marginLeft: '4px' }}>
                        {t('requests read access to dataset')}
                    </Typography.Text>
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {t('{{name}}', { name: action.dataset.name })}
                    </Link>
                    <Typography.Text style={{ marginLeft: '1px' }}>.</Typography.Text>
                </>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataProduct);
            date = action.requested_on;
            break;

        case 'data_output':
            link = createDataOutputIdPath(action.data_output_id, action.data_output.owner_id);
            description = (
                <>
                    <Typography.Text style={{ marginRight: '4px' }}>
                        {t('{{name}}, on behalf of data output', { name: action.requested_by?.first_name })}
                    </Typography.Text>
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {t('{{name}}', { name: action.data_output.name })}
                    </Link>
                    <Typography.Text style={{ marginRight: '4px', marginLeft: '4px' }}>
                        {t('requests a link to dataset ')}
                    </Typography.Text>
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {t('{{name}}', { name: action.dataset.name })}
                    </Link>
                    <Typography.Text style={{ marginLeft: '1px' }}>.</Typography.Text>
                </>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataOutput);
            date = action.requested_on;
            break;

        case 'team':
            link = createDataProductIdPath(action.data_product_id);
            description = (
                <>
                    <Typography.Text style={{ marginRight: '4px' }}>
                        {t('{{name}} would like to join the data product', { name: action.user?.first_name })}
                    </Typography.Text>
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {t('{{name}}', { name: action.data_product.name })}
                    </Link>
                    <Typography.Text style={{ marginLeft: '4px' }}>{t('team')}</Typography.Text>
                    <Typography.Text style={{ marginLeft: '1px' }}>.</Typography.Text>
                </>
            );
            navigatePath = createDataProductIdPath(action.data_product_id, DataProductTabKeys.Team);
            date = undefined;
            break;

        default:
            return null;
    }

    return {
        key: action.id,
        description: description,
        navigatePath: navigatePath,
        date: date,
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

        return [...(datasets ?? []), ...(dataOutputs ?? []), ...(dataProducts ?? [])].filter((item) => item !== null);
    }, [pendingActionsDatasets, pendingActionsDataOutputs, pendingActionsDataProducts, t]);

    const [currentPage, setCurrentPage] = useState(1);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    const paginatedItems = useMemo(() => {
        const startIndex = (currentPage - 1) * PAGE_SIZE;
        return pendingItems.slice(startIndex, startIndex + PAGE_SIZE);
    }, [currentPage, pendingItems]);

    const displayedItems = paginatedItems.length + PAGE_SIZE * (currentPage - 1);

    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>
                    {t('Pending Requests')}{' '}
                    <Typography.Text type="secondary">
                        {t('({{displayed}}/{{total}})', {
                            displayed: displayedItems,
                            total: pendingItems.length,
                        })}
                    </Typography.Text>
                </Typography.Title>
                <Pagination
                    current={currentPage}
                    pageSize={PAGE_SIZE}
                    total={pendingItems.length}
                    onChange={handlePageChange}
                    size="small"
                />
            </div>
            <div className={styles.requestsListContainer}>
                <PendingRequestsList pendingActionItems={paginatedItems} isFetching={isFetching} />
            </div>
        </div>
    );
}
