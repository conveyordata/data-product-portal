import { useCallback } from 'react';
import { useSelector } from 'react-redux';
import { InputPortTab } from '@/components/abstract-data-products/input-port-tab/input-port-tab.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    type RequestInputPortsForDataProductApiArg,
    useRequestInputPortsForDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import {
    useGetExplorationInputPortsQuery,
    useGetExplorationQuery,
    useRemoveInputPortFromExplorationMutation,
} from '@/store/api/services/generated/explorationsApi.ts';

type Props = {
    explorationId: string;
};
export const ExplorationInputPorts = ({ explorationId }: Props) => {
    const { data: { input_ports: inputPorts = [] } = {}, isFetching: loadingInputPorts } =
        useGetExplorationInputPortsQuery(explorationId);
    const currentUser = useSelector(selectCurrentUser);
    const { data: exploration } = useGetExplorationQuery(explorationId);

    const [removeInputPortFromExploration] = useRemoveInputPortFromExplorationMutation();

    const [requestInputPortsForDataProduct] = useRequestInputPortsForDataProductMutation();

    const handleRenewalRequest = useCallback(
        async (request: RequestInputPortsForDataProductApiArg) => {
            await requestInputPortsForDataProduct(request).unwrap();
        },
        [requestInputPortsForDataProduct],
    );

    const handleRemove = useCallback(
        async (outputPortId: string) => {
            await removeInputPortFromExploration({ outputPortId, id: explorationId }).unwrap();
        },
        [removeInputPortFromExploration, explorationId],
    );

    const isOwner: boolean =
        exploration !== undefined &&
        exploration?.owner !== undefined &&
        currentUser !== undefined &&
        exploration?.owner?.id === currentUser?.id;

    return (
        <InputPortTab
            loadingInputPorts={loadingInputPorts}
            canRequestAccess={isOwner}
            canRemoveAccess={isOwner}
            inputPorts={inputPorts}
            handleRemove={handleRemove}
            handleRenewalRequest={handleRenewalRequest}
            abstractDataProductId={explorationId}
        />
    );
};
