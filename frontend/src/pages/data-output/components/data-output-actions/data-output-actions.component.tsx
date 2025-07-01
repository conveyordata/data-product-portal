import { Flex } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataOutputConfigQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { useDataPlatforms } from '@/utils/data-platforms';
import styles from './data-output-actions.module.scss';

type Props = {
    dataProductId: string | undefined;
    dataOutputId: string;
};
export function DataOutputActions({ dataProductId, dataOutputId }: Props) {
    const { t } = useTranslation();
    const { data: outputYamlConfig } = useGetDataOutputConfigQuery(undefined);
    const platforms = useDataPlatforms(outputYamlConfig, t);
    const dataPlatforms = useMemo(() => platforms.filter((platform) => platform.marketplace), [platforms]);

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
