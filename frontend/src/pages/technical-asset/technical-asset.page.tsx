import { ProductOutlined, SettingOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
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
import styles from './technical-asset.module.scss';

export function TechnicalAsset() {
    const { t } = useTranslation();
    const navigate = useNavigate();
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
        return getTechnicalAssetIcon(dataOutput?.configuration.configuration_type, plugins);
    }, [dataOutput?.configuration.configuration_type, plugins]);

    const dataOutputOwners = useGetDataProductOwners(dataProduct?.id);

    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProduct?.id,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProduct },
    );
    const canEdit = edit_access?.allowed || false;

    function navigateToEditPage() {
        if (canEdit && dataOutputId && dataOutput && !isLoading) {
            navigate(
                getDynamicRoutePath(
                    ApplicationPaths.DataOutputEdit,
                    DynamicPathParams.DataOutputId,
                    dataOutputId,
                ).replace(`:${DynamicPathParams.DataProductId}`, dataOutput.owner.id),
            );
        }
    }

    if (isLoading || !dataOutput) {
        return <LoadingSpinner />;
    }

    return (
        <Flex className={styles.dataOutputContainer}>
            <Flex vertical className={styles.content}>
                <Flex className={styles.headerContainer}>
                    <Space className={styles.header}>
                        <CustomSvgIconLoader iconComponent={dataOutputTypeIcon} size="large" />
                        <Typography.Title level={3} ellipsis={{ tooltip: dataOutput?.name, rows: 2 }}>
                            {dataOutput?.name}
                        </Typography.Title>
                    </Space>
                    {canEdit && (
                        <Space className={styles.editIcon}>
                            <CircleIconButton
                                icon={<SettingOutlined />}
                                tooltip={t('Edit Technical Asset')}
                                onClick={navigateToEditPage}
                            />
                        </Space>
                    )}
                </Flex>
                {/* Main content */}
                <Flex className={styles.mainContent}>
                    {/* Data Product description */}
                    <Flex vertical className={styles.overview}>
                        <TechnicalAssetDescription
                            status={dataOutput.status}
                            namespace={dataOutput.namespace}
                            type={dataOutput.configuration.configuration_type}
                            description={dataOutput.description}
                            tags={dataOutput.tags}
                        />
                        {/*  Tabs  */}
                        <TechnicalAssetTabs
                            technicalAssetId={dataOutput.id}
                            dataProductId={dataProductId}
                            isLoading={isLoading}
                        />
                    </Flex>
                </Flex>
            </Flex>
            {/* Sidebar */}
            <Flex vertical className={styles.sidebar}>
                <TechnicalAssetActions dataProductId={dataProductId} dataOutputId={dataOutputId} />
                {/*  Data Product owners overview */}
                <UserAccessOverview users={dataOutputOwners} title={t('Technical Asset Owners')} />
            </Flex>
        </Flex>
    );
}
