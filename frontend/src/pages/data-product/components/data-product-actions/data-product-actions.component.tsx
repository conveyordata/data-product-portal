import { Flex } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { DataProductRequestAccessButton } from '@/pages/data-product/components/data-product-request-access-button/data-product-request-access-button.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import {
    useGetDataProductByIdQuery,
    useGetDataProductConveyorIDEUrlMutation,
    useGetDataProductDatabricksWorkspaceUrlMutation,
    useGetDataProductSignInUrlMutation,
    useGetDataProductSnowflakeUrlMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllPlatformsQuery } from '@/store/features/platforms/platforms-api-slice';
import { useGetDataProductRoleAssignmentsQuery } from '@/store/features/role-assignments/data-product-roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { type DataPlatform, DataPlatforms } from '@/types/data-platform';
import { DecisionStatus } from '@/types/roles';
import { getDataPlatforms } from '@/utils/data-platforms';
import styles from './data-product-actions.module.scss';

type Props = {
    dataProductId: string;
};

export function DataProductActions({ dataProductId }: Props) {
    const { t } = useTranslation();
    const user = useSelector(selectCurrentUser);
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: availablePlatforms, isLoading: isLoadingPlatforms } = useGetAllPlatformsQuery();
    const [getDataProductSignInUrl, { isLoading }] = useGetDataProductSignInUrlMutation();
    const [getConveyorUrl, { isLoading: isConveyorLoading }] = useGetDataProductConveyorIDEUrlMutation();
    const [getDatabricksWorkspaceUrl, { isLoading: isDatabricksLoading }] =
        useGetDataProductDatabricksWorkspaceUrlMutation();
    const [getSnowflakeUrl, { isLoading: isSnowflakeLoading }] = useGetDataProductSnowflakeUrlMutation();

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

    const dataPlatforms = useMemo(() => {
        const names = availablePlatforms ? availablePlatforms.map((platform) => platform.name.toLowerCase()) : [];

        return getDataPlatforms(t).filter((platform) => names.includes(platform.value));
    }, [t, availablePlatforms]);

    const { data: roleAssignments, isFetching: isFetchingRoleAssignments } = useGetDataProductRoleAssignmentsQuery({
        data_product_id: dataProductId,
        user_id: user?.id,
    });

    const allowRequesting = useMemo(() => {
        if (!user?.id || isFetchingRoleAssignments || !roleAssignments) return false;

        return !roleAssignments.some(
            ({ user: u, decision }) =>
                u.id === user.id && (decision === DecisionStatus.Pending || decision === DecisionStatus.Approved),
        );
    }, [user?.id, isFetchingRoleAssignments, roleAssignments]);

    if (!dataProduct || !user) {
        return null;
    }

    async function handleAccessToData(environment: string, dataPlatform: DataPlatform) {
        posthog.capture(PosthogEvents.DATA_PRODUCTS_PLATFORM_ACCESS, {
            platform_name: dataPlatform,
        });

        switch (dataPlatform) {
            case DataPlatforms.AWS:
                try {
                    const signInUrl = await getDataProductSignInUrl({ id: dataProductId, environment }).unwrap();
                    if (signInUrl) {
                        window.open(signInUrl, '_blank');
                    } else {
                        dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                    }
                } catch (_error) {
                    dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                }
                break;
            case DataPlatforms.Databricks:
                try {
                    const signInUrl = await getDatabricksWorkspaceUrl({ id: dataProductId, environment }).unwrap();
                    if (signInUrl) {
                        window.open(signInUrl, '_blank');
                    } else {
                        dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                    }
                } catch (_error) {
                    dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                }
                break;
            case DataPlatforms.Snowflake:
                try {
                    const signInUrl = await getSnowflakeUrl({ id: dataProductId, environment }).unwrap();
                    if (signInUrl) {
                        window.open(signInUrl, '_blank');
                    } else {
                        dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                    }
                } catch (_error) {
                    dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                }
                break;
            default:
                break;
        }
    }

    async function handleTileClick(dataPlatform: DataPlatform) {
        switch (dataPlatform) {
            case DataPlatforms.Conveyor:
                try {
                    const url = await getConveyorUrl({ id: dataProductId }).unwrap();
                    if (url) {
                        window.open(url, '_blank');
                    } else {
                        dispatchMessage({
                            type: 'error',
                            content: t('Failed to get Conveyor url'),
                        });
                    }
                } catch (_error) {
                    dispatchMessage({
                        type: 'error',
                        content: t('Failed to get Conveyor url'),
                    });
                }
                break;
            default:
                break;
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
                    isLoading={
                        isLoading ||
                        isConveyorLoading ||
                        isDatabricksLoading ||
                        isSnowflakeLoading ||
                        isLoadingPlatforms
                    }
                />
            </Flex>
        </Flex>
    );
}
