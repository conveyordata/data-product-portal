import { useCallback } from 'react';
import { useSelector } from 'react-redux';
import { InputPortTab } from '@/components/abstract-data-products/input-port-tab/input-port-tab.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    useCancelInputPortForExplorationMutation,
    useGetExplorationInputPortsQuery,
    useGetExplorationQuery,
    useRenewInputPortForExplorationMutation,
    useRevokeInputPortForExplorationMutation,
} from '@/store/api/services/generated/explorationsApi.ts';

type Props = {
    explorationId: string;
};
export const ExplorationInputPorts = ({ explorationId }: Props) => {
    const { data: { input_ports: inputPorts = [] } = {}, isFetching: loadingInputPorts } =
        useGetExplorationInputPortsQuery(explorationId);
    const currentUser = useSelector(selectCurrentUser);
    const { data: exploration } = useGetExplorationQuery(explorationId);

    const [cancelInputPortForExploration] = useCancelInputPortForExplorationMutation();
    const handleCancel = useCallback(
        async (outputPortId: string) => {
            await cancelInputPortForExploration({ outputPortId, id: explorationId }).unwrap();
        },
        [cancelInputPortForExploration, explorationId],
    );

    const [revokeInputPortForExploration] = useRevokeInputPortForExplorationMutation();
    const handleRevoke = useCallback(
        async (outputPortId: string) => {
            await revokeInputPortForExploration({ outputPortId, id: explorationId }).unwrap();
        },
        [revokeInputPortForExploration, explorationId],
    );

    const [renewInputPortForExploration] = useRenewInputPortForExplorationMutation();
    const handleRenew = useCallback(
        async (outputPortId: string) => {
            await renewInputPortForExploration({ outputPortId, id: explorationId }).unwrap();
        },
        [renewInputPortForExploration, explorationId],
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
            handleCancel={handleCancel}
            handleRevoke={handleRevoke}
            handleRenew={handleRenew}
        />
    );
};
