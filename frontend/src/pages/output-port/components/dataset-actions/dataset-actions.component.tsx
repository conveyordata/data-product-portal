import { Flex } from 'antd';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { CustomDropdownItemProps } from '@/types/shared';

import styles from './dataset-actions.module.scss';

// TODO: Catalog platforms for output ports (e.g. Collibra/Datahub) are not yet exposed
// through the backend plugin system. That system currently mixes data-product-scoped
// and output-port-scoped plugins into a single list (e.g. Coder/GitHub vs RustFS) -
// to be investigated as part of the wider plugin rework.
const dataPlatforms: CustomDropdownItemProps<string>[] = [];

type Props = {
    datasetId: string;
};
export function DatasetActions({ datasetId }: Props) {
    async function handleAccessToData(environment: string, dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
        console.log(dataPlatform, environment, datasetId);
    }

    const { data: read_integrations } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__READ_INTEGRATIONS,
        },
        {
            skip: !datasetId,
        },
    );
    const canReadIntegrations = read_integrations?.allowed ?? false;

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={canReadIntegrations}
                dataPlatforms={dataPlatforms}
                onDataPlatformClick={handleAccessToData}
                isDisabled
            />
        </Flex>
    );
}
