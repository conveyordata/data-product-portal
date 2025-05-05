import { Button, Form, List, Typography } from 'antd';
import { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DataProductDatasetLinkPopup } from '@/components/data-products/data-product-dataset-link-popup/data-product-dataset-link-popup.component.tsx';
import { DatasetTitle } from '@/components/datasets/dataset-title/dataset-title';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import {
    useGetDataProductByIdQuery,
    useRequestDatasetAccessForDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DatasetLink } from '@/types/data-product';
import { DatasetAccess, DatasetsGetContract } from '@/types/dataset';
import { SearchForm } from '@/types/shared';

import styles from './add-dataset-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataProductId: string;
};

const filterOutAlreadyAddedDatasets = (datasets: DatasetsGetContract, dataProductDatasets: DatasetLink[]) => {
    return (
        datasets.filter(
            (dataset) => !dataProductDatasets?.some((datasetLink) => datasetLink.dataset_id === dataset.id),
        ) ?? []
    );
};

const handleDatasetListFilter = (datasets: DatasetsGetContract, searchTerm: string) => {
    return datasets.filter((dataset) => {
        return dataset?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    });
};

const getIsRestrictedDataset = (dataset: DatasetsGetContract[0]) => {
    return dataset?.access_type === 'restricted';
};

const getActionButtonText = (accessType: DatasetAccess, t: TFunction) => {
    return accessType === DatasetAccess.Public ? t('Add Dataset') : t('Request Access');
};

export function AddDatasetPopup({ onClose, isOpen, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: allDatasets = [], isFetching: isFetchingDatasets } = useGetAllDatasetsQuery();
    const [requestDatasetAccessForDataProduct, { isLoading: isRequestingAccess }] =
        useRequestDatasetAccessForDataProductMutation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        const datasetLinks = dataProduct?.dataset_links ?? [];

        const unlinkedDatasets = filterOutAlreadyAddedDatasets(allDatasets, datasetLinks);
        return searchTerm ? handleDatasetListFilter(unlinkedDatasets, searchTerm) : unlinkedDatasets;
    }, [dataProduct?.dataset_links, allDatasets, searchTerm]);

    const handleRequestAccessToDataset = useCallback(
        async (datasetId: string, isRestrictedDataset?: boolean) => {
            try {
                await requestDatasetAccessForDataProduct({ dataProductId: dataProductId, datasetId }).unwrap();

                const content = isRestrictedDataset
                    ? t('Dataset access has been requested')
                    : t('Dataset has been added');
                dispatchMessage({ content, type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to request access to the data product'), type: 'error' });
            }
        },
        [dataProductId, t, requestDatasetAccessForDataProduct],
    );
    return (
        <DataProductDatasetLinkPopup
            onClose={onClose}
            isOpen={isOpen}
            searchForm={searchForm}
            title={t('Add Dataset')}
            searchPlaceholder={t('Search datasets by name')}
        >
            <List
                loading={isFetchingDatasets || isRequestingAccess}
                size={'large'}
                locale={{ emptyText: t('No datasets found') }}
                rowKey={({ id }) => id}
                dataSource={filteredDatasets}
                renderItem={(item) => {
                    const icon = <CustomSvgIconLoader iconComponent={datasetBorderIcon} />;
                    const isRestrictedDataset = getIsRestrictedDataset(item);
                    const actionButtonText = getActionButtonText(item.access_type, t);
                    return (
                        <List.Item key={item.id}>
                            <TableCellAvatar
                                icon={icon}
                                title={<DatasetTitle name={item.name} accessType={item.access_type} hasPopover />}
                                subtitle={
                                    <Typography.Link className={styles.noCursorPointer}>
                                        {item.domain.name}
                                    </Typography.Link>
                                }
                            />
                            <Button
                                disabled={isRequestingAccess}
                                loading={isRequestingAccess}
                                type={'link'}
                                onClick={() => handleRequestAccessToDataset(item.id, isRestrictedDataset)}
                            >
                                {actionButtonText}
                            </Button>
                        </List.Item>
                    );
                }}
            />
        </DataProductDatasetLinkPopup>
    );
}
