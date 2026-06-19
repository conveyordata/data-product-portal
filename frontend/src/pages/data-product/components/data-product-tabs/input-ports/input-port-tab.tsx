import { useCallback } from 'react';
import { InputPortTab } from '@/components/abstract-data-products/input-port-tab/input-port-tab.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetDataProductInputPortsQuery,
    useUnlinkInputPortFromDataProductMutation,
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

    const [removeDatasetFromDataProduct] = useUnlinkInputPortFromDataProductMutation();
    const handleRemove = useCallback(
        async (outputPortId: string) => {
            await removeDatasetFromDataProduct({ outputPortId, id: dataProductId }).unwrap();
        },
        [removeDatasetFromDataProduct, dataProductId],
    );

    return (
        <InputPortTab
            loadingInputPorts={loadingInputPorts}
            canRequestAccess={canRequestAccess?.allowed ?? false}
            canRemoveAccess={canRevokeAccess?.allowed ?? false}
            inputPorts={inputPorts}
            handleRemove={handleRemove}
        />
    );
};
