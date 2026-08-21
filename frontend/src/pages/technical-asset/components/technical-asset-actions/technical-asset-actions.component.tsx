import { Flex } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type PlatformTile,
    useGetPlatformTilesQuery,
    useLazyGetPluginUrlQuery,
} from '@/store/api/services/generated/pluginsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { CustomDropdownItemProps } from '@/types/shared';
import { dispatchMessage } from '@/utils/feedback.ts';
import { getIcon } from '@/utils/icon-loader';

import styles from './technical-asset-actions.module.scss';

type Props = {
    dataProductId: string | undefined;
};
export function TechnicalAssetActions({ dataProductId }: Props) {
    const { t } = useTranslation();

    const { data: { platform_tiles: platformTilesData } = {}, isLoading: isLoadingPlatforms } =
        useGetPlatformTilesQuery();
    const [getPluginUrl, { isLoading }] = useLazyGetPluginUrlQuery();

    const dataPlatforms = useMemo(() => {
        if (!platformTilesData) {
            return [];
        }

        const transformTile = (tile: PlatformTile): CustomDropdownItemProps<string> => ({
            label: t(tile.label),
            value: tile.value,
            icon: getIcon(tile.icon_name),
            hasEnvironments: tile.has_environments,
            hasConfig: tile.has_config,
            children: tile.children?.map(transformTile) || [],
        });

        return platformTilesData.map(transformTile);
    }, [platformTilesData, t]);

    const { data: readAccess } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS,
        },
        { skip: !dataProductId },
    );
    const canReadIntegrations = readAccess?.allowed ?? false;

    async function openPlatform(environment: string, dataPlatform: string) {
        try {
            const url = await getPluginUrl({
                id: dataProductId ?? '',
                pluginName: dataPlatform,
                environment,
            }).unwrap();
            if (url) {
                window.open(url.url, '_blank');
            } else {
                dispatchMessage({ content: t('Failed to get platform url'), type: 'error' });
            }
        } catch (_error) {
            dispatchMessage({ content: t('Failed to get platform url'), type: 'error' });
        }
    }

    async function handleTileClick(dataPlatform: string) {
        await openPlatform('', dataPlatform);
    }

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={canReadIntegrations}
                dataPlatforms={dataPlatforms}
                onDataPlatformClick={openPlatform}
                onTileClick={handleTileClick}
                isDisabled={isLoading || !canReadIntegrations}
                isLoading={isLoading || isLoadingPlatforms}
            />
        </Flex>
    );
}
