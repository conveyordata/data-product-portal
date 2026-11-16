import { Button, Flex, Input, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { searchFilter } from '@/components/empty-state/empty-state.component.tsx';
import { OutputPortOutlined } from '@/components/icons';
import { OutputPortCard } from '@/components/output-ports/output-port-card/output-port-card.component.tsx';
import { QueryList } from '@/components/query-list/query-list.component.tsx';
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
    const outputPortsQuery = useGetDataProductOutputPortsQuery(dataProductId);
    const { data: { output_ports: outputPorts = [] } = {} } = outputPortsQuery;
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductQuery(dataProductId);

    const { data: accessCreateOutputPort } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_OUTPUT_PORT,
        },
        { skip: !dataProductId },
    );

    const [searchTerm, setSearchTerm] = useState('');
    const filteredOutputPorts = useMemo(() => {
        if (!searchTerm) return outputPorts;
        return outputPorts.filter(
            (op) =>
                op?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                op?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        );
    }, [outputPorts, searchTerm]);

    if (!dataProduct) return null;

    const canCreateOutputPort = accessCreateOutputPort?.allowed ?? false;

    return (
        <Flex vertical gap={filteredOutputPorts.length === 0 ? 'large' : 'small'}>
            <Flex vertical gap="middle">
                <Flex justify="space-between" align="center">
                    <Typography.Title level={4} style={{ margin: 0 }}>
                        {t('Output Ports')}
                    </Typography.Title>
                    <Button
                        onClick={handleOpen}
                        disabled={!canCreateOutputPort}
                        type="primary"
                        loading={isLoadingDataProduct}
                    >
                        {t('Add Output Port')}
                    </Button>
                </Flex>
                <Input.Search
                    placeholder={t('Search Output Ports by name or description')}
                    allowClear
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </Flex>
            <QueryList
                query={outputPortsQuery}
                items={filteredOutputPorts}
                renderItem={(outputPort) => (
                    <OutputPortCard
                        key={outputPort.id}
                        dataProductId={dataProductId}
                        outputPortId={outputPort.id}
                        draggedDataOutputId={draggedDataOutputId}
                    />
                )}
                subject={t('Output Ports')}
                emptyState={{
                    icon: <OutputPortOutlined />,
                    title: t('No Output Ports yet'),
                    description: t('Add an Output Port to share part of this Data Product with others.'),
                }}
                filter={searchFilter(searchTerm, setSearchTerm)}
            />
            {isVisible && <AddOutputPortPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
