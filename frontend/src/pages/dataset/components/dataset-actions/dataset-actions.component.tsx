import { Flex } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataOutputConfigQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDatasetIntegrationUrlMutation } from '@/store/features/datasets/datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { RenderLocation } from '@/types/data-output/data-output-config.contract';
import { useDataPlatforms } from '@/utils/data-platforms';
import styles from './dataset-actions.module.scss';

type Props = {
    datasetId: string;
};
export function DatasetActions({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: outputYamlConfig } = useGetDataOutputConfigQuery(undefined);
    const platforms = useDataPlatforms(outputYamlConfig, t);
    const [getDatasetIntegrationUrl] = useGetDatasetIntegrationUrlMutation();
    const dataPlatforms = useMemo(
        () => platforms.filter((platform) => platform.render_at?.includes(RenderLocation.MARKETPLACE)),
        [platforms],
    );

    async function handleAccessToData(environment: string, dataPlatform: string) {
        try {
            const signInUrl = await getDatasetIntegrationUrl({
                id: datasetId,
                environment,
                integration_type: dataPlatform,
            }).unwrap();
            if (signInUrl) {
                window.open(signInUrl, '_blank');
            } else {
                dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
            }
        } catch (_error) {
            dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
        }
    }

    async function handleTileClick(dataPlatform: string) {
        handleAccessToData('default', dataPlatform);
    }

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
                onTileClick={handleTileClick}
            />
        </Flex>
    );
}
