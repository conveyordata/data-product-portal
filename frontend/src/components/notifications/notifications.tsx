import { Flex, Badge, Button, theme, Dropdown, type MenuProps, Space, Typography } from 'antd';
import { BellOutlined, ExportOutlined } from '@ant-design/icons';
import styles from './notifications.module.scss';
import { useTranslation } from 'react-i18next';
import { useCallback, useMemo } from 'react';
import { useGetDataProductDatasetPendingActionsQuery } from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { Link, type NavigateFunction, useNavigate } from 'react-router-dom';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { useGetDataOutputDatasetPendingActionsQuery } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import { useGetDataProductMembershipPendingActionsQuery } from '@/store/features/data-product-memberships/data-product-memberships-api-slice';
import { DataOutputDatasetContract } from '@/types/data-output-dataset';
import { DataProductDatasetContract } from '@/types/data-product-dataset';
import { DataProductMembershipAssociation } from '@/types/data-product-membership';
import { TFunction } from 'i18next';


export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: pending_actions_datasets } = useGetDataProductDatasetPendingActionsQuery();
    const { data: pending_actions_dataoutputs } = useGetDataOutputDatasetPendingActionsQuery();
    const { data: pending_actions_data_products } = useGetDataProductMembershipPendingActionsQuery();

    type PendingAction =
        | ({ type: 'data_product' } & DataProductDatasetContract)
        | ({ type: 'data_output' } & DataOutputDatasetContract)
        | ({ type: 'team' } & DataProductMembershipAssociation);

    const createPendingItem = useCallback((action: PendingAction, navigate: NavigateFunction, t: TFunction) => {
        let link, description, navigatePath;

        switch (action.type) {
            case 'data_product':
                link = createDataProductIdPath(action.data_product_id);
                description = (
                    <Space className={styles.description}>
                        <Typography.Text>
                            {t('{{name}}, on behalf of data product', { name: action.requested_by?.first_name })}
                        </Typography.Text>
                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                            {t('{{name}}', { name: action.data_product.name })}
                        </Link>
                        <Typography.Text>{t('requests read access to dataset')}</Typography.Text>
                        <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                            {t('{{name}}', { name: action.dataset.name })}
                        </Link>
                    </Space>
                );
                navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataProduct);
                break;

            case 'data_output':
                link = createDataOutputIdPath(action.data_output_id, action.data_output.owner_id);
                description = (
                    <Space className={styles.description}>
                        <Typography.Text>
                            {t('{{name}}, on behalf of data output', { name: action.requested_by?.first_name })}
                        </Typography.Text>
                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                            {t('{{name}}', { name: action.data_output.name })}
                        </Link>
                        <Typography.Text>{t('requests a link to dataset ')}</Typography.Text>
                        <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                            {t('{{name}}', { name: action.dataset.name })}
                        </Link>
                    </Space>
                );
                navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataOutput);
                break;

            case 'team':
                link = createDataProductIdPath(action.data_product_id);
                description = (
                    <Space className={styles.description}>
                        <Typography.Text>
                            {t('{{name}} would like to join the data product', { name: action.user?.first_name })}
                        </Typography.Text>
                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                            {t('{{name}}', { name: action.data_product.name })}
                        </Link>
                        <Typography.Text>{t('team')}</Typography.Text>
                    </Space>
                );
                navigatePath = createDataProductIdPath(action.data_product_id, DataProductTabKeys.Team);
                break;

            default:
                return null;
        }

        return {
            key: action.id,
            label: <Flex>{description}</Flex>,
            extra: <ExportOutlined />,
            onClick: () => navigate(navigatePath),
        };
    }, []);

    const pendingItems = useMemo(() => {
        const datasets = pending_actions_datasets?.map((action) =>
            createPendingItem({ ...action, type: 'data_product' }, navigate, t),
        );
        const dataOutputs = pending_actions_dataoutputs?.map((action) =>
            createPendingItem({ ...action, type: 'data_output' }, navigate, t),
        );
        const dataProducts = pending_actions_data_products?.map((action) =>
            createPendingItem({ ...action, type: 'team' }, navigate, t),
        );

        return [...(datasets ?? []), ...(dataOutputs ?? []), ...(dataProducts ?? [])];
    }, [
        pending_actions_datasets,
        pending_actions_dataoutputs,
        pending_actions_data_products,
        createPendingItem,
        navigate,
        t,
    ]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: pendingItems?.length > 0 ? t('Pending actions') : t('No pending actions'),
            children: pendingItems,
        },
    ];

    return (
        <Flex>
            <Badge
                count={pendingItems?.length}
                showZero={false}
                color={colorPrimary}
                style={{ fontSize: 10 }}
                size="small"
            >
                <Dropdown
                    placement={'bottomRight'}
                    menu={{
                        items,
                    }}
                    trigger={['click']}
                >
                    <Space>
                        <Button shape={'circle'} className={styles.iconButton} icon={<BellOutlined />} />
                    </Space>
                </Dropdown>
            </Badge>
        </Flex>
    );
}
