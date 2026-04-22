import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useGetDataProductInputPortsQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetDataProductOutputPortsQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';

export type CartOverlapCheckResult = {
    overlappingOutputPortIds: string[];
    selectedProductOutputPortsInCartIds: string[];
};

export function useCartOverlapCheck(selectedDataProductId?: string): CartOverlapCheckResult {
    const cartDatasetIds = useSelector(selectCartDatasetIds);

    const { data: { output_ports: selectedDataProductOutputPorts = [] } = {} } = useGetDataProductOutputPortsQuery(
        selectedDataProductId ?? '',
        { skip: !selectedDataProductId },
    );

    const { data: { input_ports: inputPorts = [] } = {} } = useGetDataProductInputPortsQuery(
        selectedDataProductId ?? '',
        { skip: !selectedDataProductId },
    );

    const overlappingOutputPortIds = useMemo(() => {
        return inputPorts
            .filter((link) => cartDatasetIds.includes(link.output_port_id))
            .map((link) => link.output_port_id);
    }, [cartDatasetIds, inputPorts]);

    const selectedProductOutputPortsInCartIds = useMemo(() => {
        return selectedDataProductOutputPorts.filter((ds) => cartDatasetIds.includes(ds.id)).map((ds) => ds.id);
    }, [selectedDataProductOutputPorts, cartDatasetIds]);

    return { overlappingOutputPortIds, selectedProductOutputPortsInCartIds };
}
