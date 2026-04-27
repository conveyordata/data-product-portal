import { useCallback } from 'react';
import { InputPortTab } from '@/components/abstract-data-products/input-port-tab/input-port-tab.tsx';
import { useGetExplorationInputPortsQuery } from '@/store/api/services/generated/explorationsApi.ts';

type Props = {
    explorationId: string;
};
export const ExplorationInputPorts = ({ explorationId }: Props) => {
    const { data: { input_ports: inputPorts = [] } = {}, isFetching: loadingInputPorts } =
        useGetExplorationInputPortsQuery(explorationId);

    const handleRemove = useCallback(async (_: string) => {
        return;
    }, []);

    return (
        <InputPortTab
            loadingInputPorts={loadingInputPorts}
            canRequestAccess={true}
            canRemoveAccess={false}
            inputPorts={inputPorts}
            handleRemove={handleRemove}
        />
    );
};
