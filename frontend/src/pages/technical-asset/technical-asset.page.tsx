import { ProductOutlined } from '@ant-design/icons';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router';

import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { DetailPageLayout } from '@/components/detail-page-layout/detail-page-layout.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TechnicalAssetDescription } from '@/pages/technical-asset/components/technical-asset-description/technical-asset-description.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetTechnicalAssetQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, createDataProductIdPath, DynamicPathParams } from '@/types/navigation.ts';
import { useGetDataProductOwners } from '@/utils/data-product-user-role.helper';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';
import { getTechnicalAssetIcon } from '@/utils/technical-asset-type.helper.ts';
import { TechnicalAssetActions } from './components/technical-asset-actions/technical-asset-actions.component.tsx';
import { TechnicalAssetTabs } from './components/technical-asset-tabs/technical-asset-tabs.tsx';

export function TechnicalAsset() {
    const { t } = useTranslation();
    const { dataOutputId = '', dataProductId = '' } = useParams();

    const { data: dataOutput, isLoading } = useGetTechnicalAssetQuery(
        { id: dataOutputId, dataProductId },
        { skip: !dataOutputId },
    );
    const { data: dataProduct } = useGetDataProductQuery(dataProductId, { skip: !dataProductId });
    const { data: { plugins } = {} } = useGetPluginsQuery();

    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined /> {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: <>{dataProduct?.name}</>, path: createDataProductIdPath(dataProductId) },
            { title: <>{dataOutput?.name}</> },
        ]);
    }, [setBreadcrumbs, dataProduct, dataOutput, dataProductId, t]);

    const dataOutputTypeIcon = useMemo(() => {
        return getTechnicalAssetIcon(dataOutput?.configuration.name, plugins);
    }, [dataOutput?.configuration.name, plugins]);

    const dataOutputOwners = useGetDataProductOwners(dataProduct?.id);

    const { data: updateAccess } = useCheckAccessQuery(
        {
            resource: dataProduct?.id,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
        },
        { skip: !dataProduct },
    );
    const canEdit = updateAccess?.allowed || false;

    if (isLoading || !dataOutput) {
        return <LoadingSpinner />;
    }

    return (
        <DetailPageLayout
            icon={<CustomSvgIconLoader iconComponent={dataOutputTypeIcon} size="large" />}
            title={dataOutput.name}
            edit={
                canEdit
                    ? {
                          path: getDynamicRoutePath(
                              ApplicationPaths.DataOutputEdit,
                              DynamicPathParams.DataOutputId,
                              dataOutputId,
                          ).replace(`:${DynamicPathParams.DataProductId}`, dataOutput.owner.id),
                          tooltip: t('Edit Technical Asset'),
                      }
                    : undefined
            }
            sidebar={
                <>
                    <TechnicalAssetActions dataProductId={dataProductId} dataOutputId={dataOutputId} />
                    <UserAccessOverview users={dataOutputOwners} title={t('Technical Asset Owners')} />
                </>
            }
        >
            <TechnicalAssetDescription
                status={dataOutput.status}
                namespace={dataOutput.namespace}
                type={dataOutput.configuration.name}
                description={dataOutput.description}
                tags={dataOutput.tags}
                accessModes={dataOutput.access_modes}
                environments={dataOutput.environments}
            />
            <TechnicalAssetTabs
                technicalAsset={dataOutput}
                dataProductId={dataProductId}
                canEdit={canEdit}
                isLoading={isLoading}
            />
        </DetailPageLayout>
    );
}
