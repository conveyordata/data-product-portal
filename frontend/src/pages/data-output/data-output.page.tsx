import { SettingOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';

import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { UserAccessOverview } from '@/components/data-access/user-access-overview/user-access-overview.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { DataOutputDescription } from '@/pages/data-output/components/data-output-description/data-output-description.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { getDataProductOwners, getIsDataProductOwner } from '@/utils/data-product-user-role.helper';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';

import { DataOutputActions } from './components/data-output-actions/data-output-actions.component';
import { DataOutputTabs } from './components/data-output-tabs/data-output-tabs';
import styles from './data-output.module.scss';

export function DataOutput() {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const { dataOutputId = '', dataProductId = '' } = useParams();
    const { data: dataOutput, isLoading } = useGetDataOutputByIdQuery(dataOutputId, { skip: !dataOutputId });
    const navigate = useNavigate();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });
    const dataOutputTypeIcon = useMemo(() => {
        return getDataOutputIcon(dataOutput?.configuration.configuration_type);
    }, [dataOutput?.configuration.configuration_type]);

    const dataOutputOwners = dataProduct ? getDataProductOwners(dataProduct) : [];
    const isCurrentDataOutputOwner = Boolean(
        dataProduct && currentUser && (getIsDataProductOwner(dataProduct, currentUser?.id) || currentUser?.is_admin),
    );

    function navigateToEditPage() {
        if (isCurrentDataOutputOwner && dataOutputId && dataOutput && !isLoading) {
            navigate(
                getDynamicRoutePath(
                    ApplicationPaths.DataOutputEdit,
                    DynamicPathParams.DataOutputId,
                    dataOutputId,
                ).replace(':' + DynamicPathParams.DataProductId, dataOutput.owner.id),
            );
        }
    }

    // useEffect(() => {
    //     setItemToLocalStorage(LocalStorageKeys.LastVisitedDataOutputs, {
    //         id: dataOutputId,
    //         timestamp: Date.now(),
    //     });
    // }, []);

    if (isLoading) return <LoadingSpinner />;

    // if (!dataOutput) {
    //     navigate(ApplicationPaths.DataOutputs, { replace: true });
    //     return null;
    // }

    return (
        <Flex className={styles.dataOutputContainer}>
            <Flex vertical className={styles.content}>
                <Flex className={styles.headerContainer}>
                    <Space className={styles.header}>
                        <CustomSvgIconLoader iconComponent={dataOutputTypeIcon!} size="large" />
                        <Typography.Title level={3} ellipsis={{ tooltip: dataOutput?.name, rows: 2 }}>
                            {dataOutput?.name}
                        </Typography.Title>
                    </Space>
                    {isCurrentDataOutputOwner && (
                        <Space className={styles.editIcon}>
                            <CircleIconButton
                                icon={<SettingOutlined />}
                                tooltip={t('Edit data output')}
                                onClick={navigateToEditPage}
                            />
                        </Space>
                    )}
                </Flex>
                {/* Main content */}
                <Flex className={styles.mainContent}>
                    {/* Data product description */}
                    <Flex vertical className={styles.overview}>
                        <DataOutputDescription
                            status={dataOutput!.status}
                            type={dataOutput!.configuration.configuration_type!}
                            description={dataOutput!.description}
                            tags={dataOutput!.tags}
                        />
                        {/*  Tabs  */}
                        <DataOutputTabs dataOutputId={dataOutput!.id} isLoading={isLoading} />
                    </Flex>
                </Flex>
            </Flex>
            {/* Sidebar */}
            <Flex vertical className={styles.sidebar}>
                <DataOutputActions dataOutputId={dataOutputId} isCurrentDataOutputOwner={isCurrentDataOutputOwner} />
                {/*  Data product owners overview */}
                <UserAccessOverview users={dataOutputOwners} title={t('Data Output Owners')} />
            </Flex>
        </Flex>
    );
}
