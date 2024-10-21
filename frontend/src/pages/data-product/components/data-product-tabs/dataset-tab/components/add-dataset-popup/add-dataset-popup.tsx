import { Button, Form, List, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    useGetDataProductByIdQuery,
    useRequestDatasetAccessForDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DatasetsGetContract } from '@/types/dataset';
import { useCallback, useMemo } from 'react';
import { SearchForm } from '@/types/shared';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { DatasetLink } from '@/types/data-product';
import { DataProductDatasetLinkPopup } from '@/components/data-products/data-product-dataset-link-popup/data-product-dataset-link-popup.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TFunction } from 'i18next';
import styles from './add-dataset-popup.module.scss';
import { RestrictedDatasetTitle } from '@/components/datasets/restricted-dataset-title/restricted-dataset-title.tsx';

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

const getActionButtonText = (isRestricted: boolean, t: TFunction) => {
    return isRestricted ? t('Request Access') : t('Add Dataset');
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
                    const actionButtonText = getActionButtonText(isRestrictedDataset, t);
                    return (
                        <List.Item key={item.id}>
                            <TableCellAvatar
                                icon={icon}
                                title={
                                    isRestrictedDataset ? (
                                        <RestrictedDatasetTitle name={item.name} hasPopover />
                                    ) : (
                                        item.name
                                    )
                                }
                                subtitle={
                                    <Typography.Link className={styles.noCursorPointer}>
                                        {item.business_area.name}
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
