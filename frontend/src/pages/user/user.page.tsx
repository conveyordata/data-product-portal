import { SettingOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Flex, Typography, theme } from 'antd';
import useToken from 'antd/es/theme/useToken';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component';
import { DatasetAccessIcon } from '@/components/datasets/dataset-access-icon/dataset-access-icon';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component';
import { DatasetActions } from '@/pages/dataset/components/dataset-actions/dataset-actions.component';
import { DatasetDescription } from '@/pages/dataset/components/dataset-description/dataset-description';
import { DatasetTabs } from '@/pages/dataset/components/dataset-tabs/dataset-tabs';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { useGetUserQuery } from '@/store/features/users/users-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';
import { useGetDatasetOwners } from '@/utils/dataset-user-role.helper';
import { LocalStorageKeys, setItemToLocalStorage } from '@/utils/local-storage.helper';
import { getDynamicRoutePath } from '@/utils/routes.helper';
import { UserDescription } from './components/user-description/user-description';
import styles from './user.module.scss';

export function User() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { userId = '' } = useParams();
    const {
        token: { colorErrorBorder },
    } = theme.useToken();

    const { data: user, isLoading } = useGetUserQuery(userId, { skip: !userId });
    const userInitials = user?.first_name?.charAt(0) + (user?.last_name ? user.last_name.charAt(0) : '');
    // const { data: edit_access } = useCheckAccessQuery(
    //     {
    //         resource: userId,
    //         action: AuthorizationAction.DATASET__UPDATE_PROPERTIES,
    //     },
    //     { skip: !userId },
    // );
    // const canEdit = edit_access?.allowed || false;

    // const datasetOwners = useGetDatasetOwners(dataset?.id);

    // function navigateToDatasetEditPage() {
    //     navigate(getDynamicRoutePath(ApplicationPaths.DatasetEdit, DynamicPathParams.DatasetId, datasetId));
    // }

    // useEffect(() => {
    //     setItemToLocalStorage(LocalStorageKeys.LastVisitedDatasets, {
    //         id: datasetId,
    //         timestamp: Date.now(),
    //     });
    // }, [datasetId]);

    if (isLoading) return <LoadingSpinner />;

    if (!user) return null;

    return (
        <Flex className={styles.datasetContainer}>
            <Flex vertical className={styles.datasetContent}>
                <Flex className={styles.datasetHeaderContainer}>
                    <Flex className={styles.datasetHeader}>
                        <Avatar style={{ backgroundColor: colorErrorBorder }} className={styles.avatar}>
                            {userInitials || <UserOutlined />}
                        </Avatar>
                        <Typography.Title level={3}>
                            {user.first_name} {user.last_name}
                        </Typography.Title>
                        {/* <DatasetAccessIcon accessType={dataset.access_type} hasPopover /> */}
                    </Flex>
                    {/* {canEdit && (
                        <CircleIconButton
                            icon={<SettingOutlined />}
                            tooltip={t('Edit dataset')}
                            onClick={navigateToDatasetEditPage}
                        />
                    )} */}
                </Flex>
                {/* Main content */}
                <Flex className={styles.mainContent}>
                    {/* Dataset description */}
                    <Flex vertical className={styles.datasetOverview}>
                        <UserDescription user={user} />
                        {/*  Tabs  */}
                        {/* <DatasetTabs datasetId={dataset.id} isLoading={isLoading} /> */}
                    </Flex>
                </Flex>
            </Flex>
            {/* Sidebar */}
            <Flex vertical className={styles.sidebar}>
                <></>
                {/* <DatasetActions datasetId={datasetId} /> */}
                {/*  Dataset owners overview */}
                {/* <UserAccessOverview users={datasetOwners} title={t('Dataset Owners')} /> */}
            </Flex>
        </Flex>
    );
}
