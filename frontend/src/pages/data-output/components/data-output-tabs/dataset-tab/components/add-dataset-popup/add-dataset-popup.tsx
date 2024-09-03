import { Button, Form, List, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    useGetDataOutputByIdQuery,
    useRequestDatasetAccessForDataOutputMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DatasetsGetContract } from '@/types/dataset';
import { useCallback, useMemo } from 'react';
import { SearchForm } from '@/types/shared';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { DatasetLink } from '@/types/data-output';
// import { DataOutputDatasetLinkPopup } from '@/components/data-outputs/data-output-dataset-link-popup/data-output-dataset-link-popup.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TFunction } from 'i18next';
import styles from './add-dataset-popup.module.scss';
import { RestrictedDatasetTitle } from '@/components/datasets/restricted-dataset-title/restricted-dataset-title.tsx';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataOutputId: string;
};

const filterOutAlreadyAddedDatasets = (datasets: DatasetsGetContract, dataOutputDatasets: DatasetLink[]) => {
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

const getIsRestrictedDataset = (dataset: DatasetsGetContract[0]) => {
    return dataset?.access_type === 'restricted';
};

const getActionButtonText = (isRestricted: boolean, t: TFunction) => {
    return isRestricted ? t('Request Access') : t('Add Dataset');
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
        async (datasetId: string, isRestrictedDataset?: boolean) => {
            try {
                await requestDatasetAccessForDataOutput({ dataOutputId: dataOutputId, datasetId }).unwrap();

                const content = isRestrictedDataset
                    ? t('Dataset access has been requested')
                    : t('Dataset has been added');
                dispatchMessage({ content, type: 'success' });
            } catch (error) {
                dispatchMessage({ content: t('Failed to request access to the data output'), type: 'error' });
            }
        },
        [dataOutputId, t, requestDatasetAccessForDataOutput],
    );
    return (
        <DataOutputDatasetLinkPopup
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
        </DataOutputDatasetLinkPopup>
    );
}
