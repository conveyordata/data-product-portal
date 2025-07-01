import { Flex } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataOutputConfigQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { useDataPlatforms } from '@/utils/data-platforms';
import styles from './dataset-actions.module.scss';

type Props = {
    datasetId: string;
};
export function DatasetActions({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: outputYamlConfig } = useGetDataOutputConfigQuery(undefined);
    const platforms = useDataPlatforms(outputYamlConfig, t);
    const dataPlatforms = useMemo(() => platforms.filter((platform) => platform.marketplace), [platforms]);

    async function handleAccessToData(environment: string, dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
        console.log(dataPlatform, environment, datasetId);
    }

    // const { data: request_access } = useCheckAccessQuery(
    //     {
    //         action: AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS,
    //     },
    // );
    const { data: read_integrations } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__READ_INTEGRATIONS,
        },
        {
            skip: !datasetId,
        },
    );

    // const canRequestAccess = request_access?.allowed ?? false;
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
