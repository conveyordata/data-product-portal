import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useGetDataProductInputPortsQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetDataProductOutputPortsQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetExplorationInputPortsQuery } from '@/store/api/services/generated/explorationsApi.ts';
import { selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';

export type CartOverlapCheckResult = {
    overlappingOutputPortIds: string[];
    selectedProductOutputPortsInCartIds: string[];
};

export function useCartOverlapCheck({
    selectedDataProductId,
    selectedExplorationId,
}: {
    selectedDataProductId?: string;
    selectedExplorationId?: string;
}): CartOverlapCheckResult {
    const cartDatasetIds = useSelector(selectCartDatasetIds);

    const { data: { output_ports: selectedDataProductOutputPorts = [] } = {} } = useGetDataProductOutputPortsQuery(
        selectedDataProductId ?? '',
        { skip: !selectedDataProductId },
    );

    const { data: { input_ports: dataProductInputPorts = [] } = {} } = useGetDataProductInputPortsQuery(
        selectedDataProductId ?? '',
        { skip: !selectedDataProductId },
    );

    const { data: { input_ports: explorationInputPorts = [] } = {} } = useGetExplorationInputPortsQuery(
        selectedExplorationId ?? '',
        { skip: !selectedExplorationId },
    );

    const overlappingDataProductOutputPortIds = useMemo(() => {
        return dataProductInputPorts
            .filter((link) => cartDatasetIds.includes(link.output_port_id))
            .map((link) => link.output_port_id);
    }, [cartDatasetIds, dataProductInputPorts]);

    const overlappingExplorationOutputPortIds = useMemo(() => {
        return explorationInputPorts
            .filter((link) => cartDatasetIds.includes(link.output_port_id))
            .map((link) => link.output_port_id);
    }, [cartDatasetIds, explorationInputPorts]);

    const selectedProductOutputPortsInCartIds = useMemo(() => {
        return selectedDataProductOutputPorts.filter((ds) => cartDatasetIds.includes(ds.id)).map((ds) => ds.id);
    }, [selectedDataProductOutputPorts, cartDatasetIds]);

    return {
        overlappingOutputPortIds: [...overlappingDataProductOutputPortIds, ...overlappingExplorationOutputPortIds],
        selectedProductOutputPortsInCartIds,
    };
}
