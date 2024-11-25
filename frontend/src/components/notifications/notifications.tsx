import { Flex, Badge, Button, theme, Dropdown, MenuProps, Space, Menu, Typography } from 'antd';
import { BellOutlined, ExportOutlined } from '@ant-design/icons';
import styles from './notifications.module.scss';
import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';
import { useGetDataProductDatasetPendingActionsQuery } from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { Link, useNavigate } from 'react-router-dom';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabs';
import { useGetDataOutputDatasetPendingActionsQuery } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: pending_actions_datasets } = useGetDataProductDatasetPendingActionsQuery();
    const pending_datasets = useMemo(() => {
        return pending_actions_datasets?.map((action) => {
            return {
                key: action.id,
                label: (
                    <Flex>
                        <Typography.Text style={{ marginRight: '4px' }}>
                            {t('{{name}}, on behalf of ', {name:action.requested_by?.first_name})}
                        </Typography.Text>
                        <Link
                            onClick={(e) => {
                                e.stopPropagation();
                            }}
                            to={createDataProductIdPath(action.data_product_id)}
                        >
                            {t('data product {{name}}', {name: action.data_product.name})}
                        </Link>
                        <Typography.Text style={{ marginLeft: '4px', marginRight: '4px' }}>
                            {t('requests read access to')}
                        </Typography.Text>
                        <Link onClick={(e) => {
                                e.stopPropagation();
                            }}
                         to={createDatasetIdPath(action.dataset_id)}> {t('dataset {{name}}', {name: action.dataset.name})}</Link>
                    </Flex>
                ),
                extra: <ExportOutlined/>,
                onClick: () => {
                    navigate(createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataProduct));
                },
            };
        });
    }, [pending_actions_datasets]);

    const { data: pending_actions_dataoutputs } = useGetDataOutputDatasetPendingActionsQuery();
    const pending_data_outputs = useMemo(() => {
        return pending_actions_dataoutputs?.map((action) => {
            return {
                key: action.id,
                label: (
                    <Flex>
                        <Typography.Text style={{ marginRight: '4px' }}>
                            {t('{{name}}, on behalf of ', {name:action.requested_by?.first_name})}
                        </Typography.Text>
                        <Link
                            onClick={(e) => {
                                e.stopPropagation();
                            }}
                            to={createDataOutputIdPath(action.data_output_id, action.data_output.owner_id)}
                        >
                            {t('data output {{name}}', {name: action.data_output.name})}
                        </Link>
                        <Typography.Text style={{ marginLeft: '4px', marginRight: '4px' }}>
                            {t('requests a link to')}
                        </Typography.Text>
                        <Link onClick={(e) => {
                                e.stopPropagation();
                            }}
                         to={createDatasetIdPath(action.dataset_id)}> {t('dataset {{name}}', {name: action.dataset.name})}</Link>
                    </Flex>
                ),
                extra: <ExportOutlined/>,
                onClick: () => {
                    navigate(createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataOutput));
                },
            };
        });
    }, [pending_actions_dataoutputs]);

    const total_items = useMemo(() => {
        return pending_datasets?.concat(pending_data_outputs ?? []);
    }, [pending_datasets, pending_data_outputs]);
    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: t('Pending actions'),
            children: total_items,
        },
    ];

    return (
        <Flex>
            <Badge
                count={total_items?.length}
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
                    // {...dropdownProps}
                >
                    <Space>
                        <Button
                            shape={'circle'}
                            className={styles.iconButton}
                            icon={<BellOutlined />}
                            onClick={() => {
                                console.log('clicked');
                            }}
                        />
                    </Space>
                </Dropdown>
            </Badge>
        </Flex>
    );
}
