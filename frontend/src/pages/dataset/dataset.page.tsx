import { SettingOutlined } from '@ant-design/icons';
import { Flex, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { DatasetAccessIcon } from '@/components/datasets/dataset-access-icon/dataset-access-icon';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DatasetActions } from '@/pages/dataset/components/dataset-actions/dataset-actions.tsx';
import { DatasetDescription } from '@/pages/dataset/components/dataset-description/dataset-description.tsx';
import { DatasetTabs } from '@/pages/dataset/components/dataset-tabs/dataset-tabs.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper.ts';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';

import styles from './dataset.module.scss';

export function Dataset() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { datasetId = '' } = useParams();
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const currentUser = useSelector(selectCurrentUser);

    const datasetOwners = useMemo(() => dataset?.owners || [], [dataset?.owners]);
    const isDatasetOwner = useMemo(
        () => datasetOwners.some((owner) => owner.id === currentUser?.id) || Boolean(currentUser?.is_admin),
        [datasetOwners, currentUser],
    );
    const { data: access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const canEditNew = access?.allowed || false;

    function navigateToDatasetEditPage() {
        if (canEditNew || (isDatasetOwner && datasetId)) {
            navigate(getDynamicRoutePath(ApplicationPaths.DatasetEdit, DynamicPathParams.DatasetId, datasetId));
        }
    }

    useEffect(() => {
        setItemToLocalStorage(LocalStorageKeys.LastVisitedDatasets, {
            id: datasetId,
            timestamp: Date.now(),
        });
    }, [datasetId]);

    if (isLoading) return <LoadingSpinner />;

    if (!dataset) return null;

    return (
        <Flex className={styles.datasetContainer}>
            <Flex vertical className={styles.datasetContent}>
                <Flex className={styles.datasetHeaderContainer}>
                    <Flex className={styles.datasetHeader}>
                        <CustomSvgIconLoader iconComponent={datasetBorderIcon} size="large" />
                        <Typography.Title level={3}>{dataset?.name}</Typography.Title>
                        <DatasetAccessIcon accessType={dataset.access_type} hasPopover />
                    </Flex>
                    {(canEditNew || isDatasetOwner) && (
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
                            domain={dataset.domain.name}
                            accessType={getDatasetAccessTypeLabel(t, dataset.access_type)}
                            tags={[
                                ...dataset.tags,
                                ...dataset.rolled_up_tags.map((tag) => ({ rolled_up: true, ...tag })),
                            ]}
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
