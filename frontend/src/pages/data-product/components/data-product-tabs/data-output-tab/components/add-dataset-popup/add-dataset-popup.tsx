import { Button, Form, List, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DataProductDatasetLinkPopup } from '@/components/data-products/data-product-dataset-link-popup/data-product-dataset-link-popup.component.tsx';
import { DatasetTitle } from '@/components/datasets/dataset-title/dataset-title';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import {
    useGetDataOutputByIdQuery,
    useRequestDatasetAccessForDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataOutputDatasetLink } from '@/types/data-output/dataset-link.contract';
import { DatasetsGetContract } from '@/types/dataset';
import { SearchForm } from '@/types/shared';

import styles from './add-dataset-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataOutputId: string;
};

const filterOutAlreadyAddedDatasets = (datasets: DatasetsGetContract, dataOutputDatasets: DataOutputDatasetLink[]) => {
    return (
        datasets.filter(
            (dataset) => !dataOutputDatasets?.some((datasetLink) => datasetLink.dataset_id === dataset.id),
        ) ?? []
    );
};

const handleDatasetListFilter = (datasets: DatasetsGetContract, searchTerm: string) => {
    return datasets.filter((dataset) => {
        return dataset?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    });
};

const getActionButtonText = (t: TFunction) => {
    return t('Request Link');
};

export function AddDatasetPopup({ onClose, isOpen, dataOutputId }: Props) {
    const { t } = useTranslation();
    const { data: dataOutput } = useGetDataOutputByIdQuery(dataOutputId);
    const { data: allDatasets = [], isFetching: isFetchingDatasets } = useGetAllDatasetsQuery();
    const [requestDatasetAccessForDataOutput, { isLoading: isRequestingAccess }] =
        useRequestDatasetAccessForDataOutputMutation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        const datasetLinks = dataOutput?.dataset_links ?? [];

        const unlinkedDatasets = filterOutAlreadyAddedDatasets(allDatasets, datasetLinks);
        return searchTerm ? handleDatasetListFilter(unlinkedDatasets, searchTerm) : unlinkedDatasets;
    }, [dataOutput?.dataset_links, allDatasets, searchTerm]);

    const handleRequestAccessToDataset = useCallback(
        async (datasetId: string) => {
            try {
                await requestDatasetAccessForDataOutput({ dataOutputId: dataOutputId, datasetId }).unwrap();

                const content = t('Dataset link has been requested');
                dispatchMessage({ content, type: 'success' });
                onClose();
            } catch (_error) {
                dispatchMessage({ content: t('Failed to link dataset to data output'), type: 'error' });
            }
        },
        [requestDatasetAccessForDataOutput, dataOutputId, t, onClose],
    );

    return (
        <DataProductDatasetLinkPopup
            onClose={onClose}
            isOpen={isOpen}
            searchForm={searchForm}
            title={t('Link Dataset')}
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
                    const actionButtonText = getActionButtonText(t);
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
                                onClick={() => handleRequestAccessToDataset(item.id)}
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
