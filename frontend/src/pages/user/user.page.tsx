import { UserOutlined } from '@ant-design/icons';
import { Avatar, Flex, Typography, theme } from 'antd';
import { useParams } from 'react-router';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetUserQuery } from '@/store/features/users/users-api-slice';
import { UserDescription } from './components/user-description/user-description';
import styles from './user.module.scss';

export function User() {
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
