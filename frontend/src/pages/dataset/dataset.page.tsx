import { useNavigate, useParams } from 'react-router-dom';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import styles from './dataset.module.scss';
import { Flex, Popover, Typography } from 'antd';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { DatasetTabs } from '@/pages/dataset/components/dataset-tabs/dataset-tabs.tsx';
import { DatasetDescription } from '@/pages/dataset/components/dataset-description/dataset-description.tsx';
import { useEffect, useMemo } from 'react';
import { SettingOutlined } from '@ant-design/icons';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';
import { DatasetActions } from '@/pages/dataset/components/dataset-actions/dataset-actions.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper.ts';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';

export function Dataset() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { datasetId = '' } = useParams();
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const currentUser = useSelector(selectCurrentUser);

    const datasetOwners = useMemo(() => dataset?.owners || [], [dataset?.owners]);
    const isDatasetOwner = useMemo(
        () => datasetOwners.some((owner) => owner.id === currentUser?.id) || Boolean(currentUser?.is_admin),
        [datasetOwners, currentUser?.id],
    );

    function navigateToDatasetEditPage() {
        if (isDatasetOwner && datasetId) {
            navigate(getDynamicRoutePath(ApplicationPaths.DatasetEdit, DynamicPathParams.DatasetId, datasetId));
        }
    }

    useEffect(() => {
        setItemToLocalStorage(LocalStorageKeys.LastVisitedDatasets, {
            id: datasetId,
            timestamp: Date.now(),
        });
    }, []);

    if (isLoading) return <LoadingSpinner />;

    if (!dataset) return null;

    return (
        <Flex className={styles.datasetContainer}>
            <Flex vertical className={styles.datasetContent}>
                <Flex className={styles.datasetHeaderContainer}>
                    <Flex className={styles.datasetHeader}>
                        <CustomSvgIconLoader iconComponent={datasetBorderIcon} size="large" />
                        <Typography.Title level={3}>{dataset?.name}</Typography.Title>
                        {dataset.access_type === 'restricted' && (
                            <Popover content={t('Restricted access')} trigger="hover">
                                <Flex>
                                    <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="x-small" color={'dark'} />
                                </Flex>
                            </Popover>
                        )}
                    </Flex>
                    {isDatasetOwner && (
                        <CircleIconButton
                            icon={<SettingOutlined />}
                            tooltip={t('Edit dataset')}
                            onClick={navigateToDatasetEditPage}
                        />
                    )}
                </Flex>
                {/* Main content */}
                <Flex className={styles.mainContent}>
                    {/* Dataset description */}
                    <Flex vertical className={styles.datasetOverview}>
                        <DatasetDescription
                            lifecycle={dataset.lifecycle}
                            description={dataset.description}
                            businessArea={dataset.business_area.name}
                            accessType={getDatasetAccessTypeLabel(dataset.access_type)}
                        />
                        {/*  Tabs  */}
                        <DatasetTabs datasetId={dataset.id} isLoading={isLoading} />
                    </Flex>
                </Flex>
            </Flex>
            {/* Sidebar */}
            <Flex vertical className={styles.sidebar}>
                <DatasetActions datasetId={datasetId} isCurrentDatasetOwner={isDatasetOwner} />
                {/*  Dataset owners overview */}
                <UserAccessOverview users={datasetOwners} title={t('Dataset Owners')} />
            </Flex>
        </Flex>
    );
}
