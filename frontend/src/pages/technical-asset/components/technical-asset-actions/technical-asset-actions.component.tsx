import { Flex } from 'antd';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { CustomDropdownItemProps } from '@/types/shared';

import styles from './technical-asset-actions.module.scss';

// TODO: Catalog platforms for technical assets (e.g. Collibra/Datahub) are not yet exposed
// through the backend plugin system. That system currently mixes data-product-scoped
// and output-port-scoped plugins into a single list (e.g. Coder/GitHub vs RustFS) -
// to be investigated as part of the wider plugin rework.
const dataPlatforms: CustomDropdownItemProps<string>[] = [];

type Props = {
    dataProductId: string | undefined;
    dataOutputId: string;
};
export function TechnicalAssetActions({ dataProductId, dataOutputId }: Props) {
    async function handleAccessToData(environment: string, dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
        console.log(dataPlatform, environment, dataOutputId);
    }

    const { data: readAccess } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS,
        },
        { skip: !dataProductId },
    );

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={readAccess?.allowed ?? false}
                dataPlatforms={dataPlatforms}
                onDataPlatformClick={handleAccessToData}
                isDisabled
            />
        </Flex>
    );
}
