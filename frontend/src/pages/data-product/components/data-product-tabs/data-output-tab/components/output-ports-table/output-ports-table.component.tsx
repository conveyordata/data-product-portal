import { Button, Flex, Input, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DatasetCard } from '@/components/datasets/dataset-card/dataset-card.component';
import { useModal } from '@/hooks/use-modal';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetDataProductOutputPortsQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { AddOutputPortPopup } from '../add-output-port-popup/add-output-port-popup';

type Props = {
    dataProductId: string;
    draggedDataOutputId?: string | null;
};

export function OutputPortsTable({ dataProductId, draggedDataOutputId }: Props) {
    const { t } = useTranslation();
    const { data: { output_ports: outputPorts = [] } = {} } = useGetDataProductOutputPortsQuery(dataProductId);
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductQuery(dataProductId);

    const { data: access_create_dataset } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.GLOBAL__CREATE_OUTPUT_PORT,
        },
        { skip: !dataProductId },
    );

    const { data: can_link_data_output } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
        },
        { skip: !dataProductId },
    );
    const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
    const filteredDatasets = useMemo(() => {
        if (!searchTerm) return outputPorts;
        return outputPorts.filter(
            (dataset) =>
                dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        );
    }, [outputPorts, searchTerm]);

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
                <Input.Search
                    placeholder={t('Search Output Ports by name or description')}
                    allowClear
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </Flex>
            {filteredDatasets.map((dataset) => (
                <DatasetCard
                    key={dataset.id}
                    dataProductId={dataProductId}
                    datasetId={dataset.id}
                    draggedDataOutputId={draggedDataOutputId}
                />
            ))}
            {filteredDatasets.length === 0 && (
                <Flex justify={'center'}>
                    <Typography.Text type="secondary">
                        {searchTerm ? t('No Output Ports found matching your search') : t('No Output Ports found')}
                    </Typography.Text>
                </Flex>
            )}
            {isVisible && <AddOutputPortPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
