import { ProductOutlined } from '@ant-design/icons';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

import { IdentityAccessOverview } from '@/components/data-access/identity-access-overview/identity-access-overview.component.tsx';
import { DataProductVisibilityIcon } from '@/components/data-products/data-product-visibility-icon.tsx';
import { DetailPageLayout } from '@/components/detail-page-layout/detail-page-layout.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataProductActions } from '@/pages/data-product/components/data-product-actions/data-product-actions.component.tsx';
import { DataProductDescription } from '@/pages/data-product/components/data-product-description/data-product-description.tsx';
import { DataProductTabs } from '@/pages/data-product/components/data-product-tabs/data-product-tabs.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetDataProductQuery,
    useGetDataProductRolledUpTagsQuery,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { useGetDataProductOwners } from '@/utils/data-product-role.helper.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';

export function DataProduct() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { dataProductId = '' } = useParams();

    const { data: dataProduct, isFetching: isFetchingDataProduct } = useGetDataProductQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined />
                        {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: dataProduct?.name },
        ]);
    }, [setBreadcrumbs, dataProduct, t]);
    const { data: { rolled_up_tags: rolledUpTags = [] } = {} } = useGetDataProductRolledUpTagsQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );

    const canEdit = edit_access?.allowed || false;

    const dataProductTypeIcon = useMemo(() => {
        return getDataProductTypeIcon(dataProduct?.type?.icon_key);
    }, [dataProduct?.type?.icon_key]);

    const dataProductOwners = useGetDataProductOwners(dataProduct?.id);

    //Only show the spinner when we have no data product to show, if we have one, we want to continue
    //Otherwise updating the settings for examples updates the whole page to a spinner, which is very weird
    if (isFetchingDataProduct && !dataProduct) return <LoadingSpinner />;

    if (!dataProduct) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    return (
        <DetailPageLayout
            icon={<CustomSvgIconLoader iconComponent={dataProductTypeIcon} hasRoundBorder />}
            title={dataProduct.name}
            titleExtra={<DataProductVisibilityIcon visibility={dataProduct.visibility} />}
            edit={
                canEdit
                    ? {
                          path: getDynamicRoutePath(
                              ApplicationPaths.DataProductEdit,
                              DynamicPathParams.DataProductId,
                              dataProductId,
                          ),
                          tooltip: t('Edit Data Product'),
                      }
                    : undefined
            }
            sidebar={
                <>
                    <DataProductActions dataProductId={dataProductId} />
                    <IdentityAccessOverview identities={dataProductOwners} title={t('Data Product Owners')} />
                </>
            }
        >
            <DataProductDescription
                lifecycle={dataProduct.lifecycle}
                type={dataProduct.type.name}
                description={dataProduct.description}
                domain={dataProduct.domain.name}
                namespace={dataProduct.namespace}
                environments={dataProduct.environments}
                tags={[...dataProduct.tags, ...rolledUpTags.map((tag) => ({ rolled_up: true, ...tag }))]}
            />
            <DataProductTabs dataProductId={dataProduct.id} />
        </DetailPageLayout>
    );
}
