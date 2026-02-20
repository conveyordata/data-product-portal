import { EditOutlined, ProductOutlined, ShopOutlined } from '@ant-design/icons';
import { Flex, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, useParams } from 'react-router';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component';
import { OutputPortAccessIcon } from '@/components/datasets/output-port-access-icon/output-port-access-icon.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { DatasetActions } from '@/pages/dataset/components/dataset-actions/dataset-actions.component';
import { OutputPortDescription } from '@/pages/dataset/components/dataset-description/output-port-description.tsx';
import { DatasetQuality } from '@/pages/dataset/components/dataset-quality/dataset-quality.component.tsx';
import { DatasetTabs } from '@/pages/dataset/components/dataset-tabs/dataset-tabs';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, createDataProductIdPath, DynamicPathParams } from '@/types/navigation';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';
import { useGetDatasetOwners } from '@/utils/dataset-user-role.helper';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper';
import styles from './dataset.module.scss';

export function Dataset() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { datasetId = '', dataProductId = '' } = useParams();

    const { data: outputPort, isLoading } = useGetOutputPortQuery(
        { dataProductId, id: datasetId },
        { skip: !dataProductId || !datasetId },
    );
    const { data: data_product, isLoading: isLoadingDataProduct } = useGetDataProductQuery(dataProductId, {
        skip: !dataProductId,
    });
    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const canEdit = edit_access?.allowed || false;
    const { pathname } = useLocation();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        if (pathname.includes('studio')) {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            <ProductOutlined /> {t('Product Studio')}
                        </>
                    ),
                    path: ApplicationPaths.Studio,
                },
                { title: <>{data_product?.name}</>, path: createDataProductIdPath(dataProductId) },
                { title: <>{outputPort?.name}</> },
            ]);
        } else {
            setBreadcrumbs([
                {
                    title: (
                        <>
                            {' '}
                            <ShopOutlined /> {t('Marketplace')}
                        </>
                    ),
                    path: ApplicationPaths.Marketplace,
                },
                { title: <>{data_product?.name}</>, path: createDataProductIdPath(dataProductId) },
                { title: <>{outputPort?.name}</> },
            ]);
        }
    }, [setBreadcrumbs, data_product, outputPort, dataProductId, pathname, t]);

    const datasetOwners = useGetDatasetOwners(outputPort?.id);

    function navigateToDatasetEditPage() {
        navigate(
            ApplicationPaths.MarketPlaceOutputPortEdit.replace(`:${DynamicPathParams.DatasetId}`, datasetId).replace(
                `:${DynamicPathParams.DataProductId}`,
                dataProductId,
            ),
        );
    }

    useEffect(() => {
        setItemToLocalStorage(LocalStorageKeys.LastVisitedDatasets, {
            id: datasetId,
            timestamp: Date.now(),
        });
    }, [datasetId]);

    if (isLoading || isLoadingDataProduct) return <LoadingSpinner />;

    if (!outputPort || !data_product) return null;

    return (
        <Flex className={styles.datasetContainer}>
            <Flex vertical className={styles.datasetContent}>
                <Flex className={styles.datasetHeaderContainer}>
                    <Flex className={styles.datasetHeader}>
                        <CustomSvgIconLoader iconComponent={datasetBorderIcon} size="large" />
                        <Typography.Title level={3}>{outputPort?.name}</Typography.Title>
                        <OutputPortAccessIcon accessType={outputPort.access_type} hasPopover />
                    </Flex>
                    {canEdit && (
                        <CircleIconButton
                            icon={<EditOutlined />}
                            tooltip={t('Edit Output Port')}
                            onClick={navigateToDatasetEditPage}
                        />
                    )}
                </Flex>
                {/* Main content */}
                <Flex className={styles.mainContent}>
                    {/* Dataset description */}
                    <Flex vertical className={styles.datasetOverview}>
                        <OutputPortDescription
                            lifecycle={outputPort.lifecycle}
                            data_product={data_product}
                            description={outputPort.description}
                            domain={outputPort.domain.name}
                            namespace={outputPort.namespace}
                            accessType={getDatasetAccessTypeLabel(t, outputPort.access_type)}
                            tags={[
                                ...outputPort.tags,
                                ...outputPort.rolled_up_tags.map((tag) => ({ rolled_up: true, ...tag })),
                            ]}
                        />
                        {/*  Tabs  */}
                        <DatasetTabs datasetId={outputPort.id} dataProductId={dataProductId} isLoading={isLoading} />
                    </Flex>
                </Flex>
            </Flex>
            {/* Sidebar */}
            <Flex vertical className={styles.sidebar}>
                <DatasetActions datasetId={datasetId} />
                <DatasetQuality dataProductId={outputPort?.data_product_id} datasetId={datasetId} />
                <UserAccessOverview users={datasetOwners} title={t('Output Port Owners')} />
            </Flex>
        </Flex>
    );
}
