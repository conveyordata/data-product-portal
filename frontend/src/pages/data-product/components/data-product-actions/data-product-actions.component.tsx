import { usePostHog } from '@posthog/react';
import { Flex } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { PosthogEvents } from '@/constants/posthog.constants';
import { DataProductRequestAccessButton } from '@/pages/data-product/components/data-product-request-access-button/data-product-request-access-button.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useListDataProductRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import {
    type PlatformTile,
    useGetPlatformTilesQuery,
    useLazyGetPluginUrlQuery,
} from '@/store/api/services/generated/pluginsApi';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DecisionStatus } from '@/types/roles';
import type { CustomDropdownItemProps } from '@/types/shared';
import { getIcon } from '@/utils/icon-loader';
import styles from './data-product-actions.module.scss';

type Props = {
    dataProductId: string;
};

export function DataProductActions({ dataProductId }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();

    const user = useSelector(selectCurrentUser);
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: { platform_tiles: platformTilesData } = {}, isLoading: isLoadingPlatforms } =
        useGetPlatformTilesQuery();

    const [getPluginUrl, { isLoading }] = useLazyGetPluginUrlQuery();

    const { data: request_access } = useCheckAccessQuery({
        action: AuthorizationAction.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
    });
    const { data: read_integrations } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS,
        },
        {
            skip: !dataProductId,
        },
    );

    const canRequestAccess = request_access?.allowed ?? false;
    const canReadIntegrations = read_integrations?.allowed ?? false;

    // Transform backend tiles to frontend format
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

    const { data: roleAssignments, isFetching: isFetchingRoleAssignments } = useListDataProductRoleAssignmentsQuery({
        dataProductId: dataProductId,
        userId: user?.id,
    });

    const allowRequesting = useMemo(() => {
        if (!user?.id || isFetchingRoleAssignments || !roleAssignments) return false;

        return !roleAssignments?.role_assignments?.some(
            ({ user: u, decision }) =>
                u.id === user.id && (decision === DecisionStatus.Pending || decision === DecisionStatus.Approved),
        );
    }, [user?.id, isFetchingRoleAssignments, roleAssignments]);

    if (!dataProduct || !user) {
        return null;
    }

    async function handleAccessToData(_environment: string, dataPlatform: string) {
        posthog.capture(PosthogEvents.DATA_PRODUCTS_PLATFORM_ACCESS, {
            platform_name: dataPlatform,
        });

        try {
            const url = await getPluginUrl({
                id: dataProductId,
                environment: _environment,
                pluginName: dataPlatform,
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
        try {
            const url = await getPluginUrl({ id: dataProductId, pluginName: dataPlatform }).unwrap();
            if (url) {
                window.open(url.url, '_blank');
            } else {
                dispatchMessage({
                    type: 'error',
                    content: t('Failed to get platform url'),
                });
            }
        } catch (_error) {
            dispatchMessage({
                type: 'error',
                content: t('Failed to get platform url'),
            });
        }
    }

    return (
        <Flex vertical className={styles.actionsContainer}>
            {canRequestAccess && allowRequesting && (
                <DataProductRequestAccessButton dataProductId={dataProductId} userId={user.id} />
            )}
            <Flex vertical className={styles.accessDataContainer}>
                <DataAccessTileGrid
                    canAccessData={canReadIntegrations}
                    dataPlatforms={dataPlatforms}
                    onDataPlatformClick={handleAccessToData}
                    onTileClick={handleTileClick}
                    isDisabled={isLoading || !canReadIntegrations}
                    isLoading={isLoading || isLoadingPlatforms}
                />
            </Flex>
        </Flex>
    );
}
