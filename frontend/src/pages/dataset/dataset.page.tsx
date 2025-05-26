import { SettingOutlined } from '@ant-design/icons';
import { Flex, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component';
import { DatasetAccessIcon } from '@/components/datasets/dataset-access-icon/dataset-access-icon';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { DatasetActions } from '@/pages/dataset/components/dataset-actions/dataset-actions.component';
import { DatasetDescription } from '@/pages/dataset/components/dataset-description/dataset-description';
import { DatasetTabs } from '@/pages/dataset/components/dataset-tabs/dataset-tabs';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';
import { useGetDatasetOwners } from '@/utils/dataset-user-role.helper';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper';
import { getDynamicRoutePath } from '@/utils/routes.helper';

import styles from './dataset.module.scss';

export function Dataset() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { datasetId = '' } = useParams();

    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const canEdit = edit_access?.allowed || false;

    const datasetOwners = useGetDatasetOwners(dataset?.id);

    function navigateToDatasetEditPage() {
        navigate(getDynamicRoutePath(ApplicationPaths.DatasetEdit, DynamicPathParams.DatasetId, datasetId));
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
                    {(canEdit) && (
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
                <DatasetActions datasetId={datasetId} />
                {/*  Dataset owners overview */}
                <UserAccessOverview users={datasetOwners} title={t('Dataset Owners')} />
            </Flex>
        </Flex>
    );
}
