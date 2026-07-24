import { useCallback } from 'react';
import { InputPortTab } from '@/components/abstract-data-products/input-port-tab/input-port-tab.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useCancelInputPortForDataProductMutation,
    useGetDataProductInputPortsQuery,
    useRenewInputPortForDataProductMutation,
    useRevokeInputPortForDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';

type Props = {
    dataProductId: string;
};
export const DataProductInputPorts = ({ dataProductId }: Props) => {
    const { data: { input_ports: inputPorts = [] } = {}, isFetching: loadingInputPorts } =
        useGetDataProductInputPortsQuery(dataProductId);
    const { data: canRequestAccess } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
        },
        { skip: !dataProductId },
    );

    const { data: canRevokeAccess } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
        },
        { skip: !dataProductId },
    );

    const [cancelInputPortForDataProduct] = useCancelInputPortForDataProductMutation();
    const handleCancel = useCallback(
        async (outputPortId: string) => {
            await cancelInputPortForDataProduct({ outputPortId, id: dataProductId }).unwrap();
        },
        [cancelInputPortForDataProduct, dataProductId],
    );

    const [revokeInputPortForDataProduct] = useRevokeInputPortForDataProductMutation();
    const handleRevoke = useCallback(
        async (outputPortId: string) => {
            await revokeInputPortForDataProduct({ outputPortId, id: dataProductId }).unwrap();
        },
        [revokeInputPortForDataProduct, dataProductId],
    );

    const [renewInputPortForDataProduct] = useRenewInputPortForDataProductMutation();
    const handleRenew = useCallback(
        async (outputPortId: string) => {
            await renewInputPortForDataProduct({ outputPortId, id: dataProductId }).unwrap();
        },
        [renewInputPortForDataProduct, dataProductId],
    );

    return (
        <InputPortTab
            loadingInputPorts={loadingInputPorts}
            canRequestAccess={canRequestAccess?.allowed ?? false}
            canRemoveAccess={canRevokeAccess?.allowed ?? false}
            inputPorts={inputPorts}
            handleCancel={handleCancel}
            handleRevoke={handleRevoke}
            handleRenew={handleRenew}
        />
    );
};
