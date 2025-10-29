import { Button, Flex, Form, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { DatasetCard } from '@/components/datasets/dataset-card/dataset-card.component';
import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract.ts';
import type { SearchForm } from '@/types/shared';
import { AddOutputPortPopup } from '../add-output-port-popup/add-output-port-popup';
import styles from './dataset-table.module.scss';

type Props = {
    dataProductId: string;
    datasets: DatasetsGetContract;
    draggedDataOutputId?: string | null;
};

export function DatasetTable({ dataProductId, datasets, draggedDataOutputId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    const { data: access_create_dataset } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.GLOBAL__CREATE_DATASET,
        },
        { skip: !dataProductId },
    );
    const { data: can_link_data_output } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
        },
        { skip: !dataProductId },
    );
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredDatasets = useMemo(() => {
        if (!searchTerm) return datasets;
        return datasets.filter(
            (dataset) =>
                dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        );
    }, [datasets, searchTerm]);

    if (!dataProduct) return null;

    // TODO To be seen if these are the right ACCESS checks we want here or if we need to create new ones.
    const canCreateDataset = (access_create_dataset?.allowed && can_link_data_output?.allowed) || false;

    return (
        <Flex vertical gap={filteredDatasets.length === 0 ? 'large' : 'small'}>
            <Flex vertical gap="middle">
                <Flex justify="space-between" align="center">
                    <Typography.Title level={4} style={{ margin: 0 }}>
                        {t('Output Ports')}
                    </Typography.Title>
                    <Button
                        onClick={handleOpen}
                        disabled={!canCreateDataset}
                        type="primary"
                        loading={isLoadingDataProduct}
                    >
                        {t('Add Output Port')}
                    </Button>
                </Flex>

                <Searchbar
                    placeholder={t('Search output ports by name or description')}
                    formItemProps={{ initialValue: '', className: styles.searchBar }}
                    form={searchForm}
                />
            </Flex>

            {filteredDatasets.map((dataset) => (
                <DatasetCard key={dataset.id} datasetId={dataset.id} draggedDataOutputId={draggedDataOutputId} />
            ))}

            {filteredDatasets.length === 0 && (
                <Flex justify={'center'}>
                    <Typography.Text type="secondary">
                        {searchTerm ? t('No output ports found matching your search') : t('No output ports found')}
                    </Typography.Text>
                </Flex>
            )}
            {isVisible && <AddOutputPortPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
