import { DeleteOutlined, WarningOutlined } from '@ant-design/icons';
import { Button, Card, Descriptions, Flex, List, Space, Tag, Tooltip, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useAppDispatch } from '@/store';
import { removeDatasetFromCart } from '@/store/features/cart/cart-slice.ts';
import type { DatasetsGetContractSingle } from '@/types/dataset/datasets-get.contract.ts';
import { createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { useGetDataProductOwners } from '@/utils/data-product-user-role.helper.ts';

type CartOverviewItemProps = {
    dataset: DatasetsGetContractSingle;
    overlapping?: boolean;
    selectedDataProductId?: string;
};

function CartOverviewItem({ dataset, overlapping, selectedDataProductId }: CartOverviewItemProps) {
    const { t } = useTranslation();
    const dataProductOwners = useGetDataProductOwners(dataset.data_product_id);

    const warningTooltip = useMemo(() => {
        if (selectedDataProductId === dataset.data_product_id) {
            return t('You can not request access to your own output ports');
        }
        if (overlapping) {
            return t('The selected data product already has access, or an access request open for this output port');
        }
        return null;
    }, [selectedDataProductId, dataset.data_product_id, overlapping, t]);

    const renderOwners = () => {
        if (!dataProductOwners || dataProductOwners.length === 0) return null;

        let maxVisible = 2;
        if (dataProductOwners.length > maxVisible) {
            //We want to show at max 2 owners, but if we have more than 2, we show only 1, and show +x more
            maxVisible = 1;
        }
        const visibleOwners = dataProductOwners.slice(0, maxVisible);
        const remainingCount = dataProductOwners.length - maxVisible;

        return (
            <Space size="small" wrap>
                {visibleOwners.map((owner) => (
                    <Tag key={owner.id}>{owner.email}</Tag>
                ))}
                {remainingCount > 0 && (
                    <Tooltip
                        title={
                            <Space orientation="vertical" size={'small'}>
                                {dataProductOwners.slice(maxVisible).map((owner) => (
                                    <span key={owner.id}>{owner.email}</span>
                                ))}
                            </Space>
                        }
                    >
                        <Tag style={{ cursor: 'pointer' }}>+{remainingCount} more</Tag>
                    </Tooltip>
                )}
            </Space>
        );
    };
    return (
        <Descriptions
            title={
                <Tooltip title={warningTooltip}>
                    <Space size="small">
                        <Link to={createDatasetIdPath(dataset.id)} target={'_blank'}>
                            <Typography.Text>{dataset.name}</Typography.Text>
                        </Link>
                        {warningTooltip !== null && (
                            <CustomSvgIconLoader size={'x-small'} iconComponent={WarningOutlined} color={'warning'} />
                        )}
                    </Space>
                </Tooltip>
            }
            column={1}
            size={'small'}
            items={[
                {
                    key: 'data product',
                    label: <Typography.Text strong>{t('Data product')}</Typography.Text>,
                    children: (
                        <Link to={createDataProductIdPath(dataset.data_product_id)} target={'_blank'}>
                            <Typography.Text>{dataset.data_product_name}</Typography.Text>
                        </Link>
                    ),
                },
                {
                    key: 'owner',
                    label: <Typography.Text strong>{t('Owner')}</Typography.Text>,
                    children: renderOwners(),
                },
            ]}
        />
    );
}

type CartOverviewProps = {
    cartDatasets?: DatasetsGetContractSingle[];
    overlappingDatasetIds?: string[];
    loading?: boolean;
    selectedDataProductId?: string;
};

export const CartOverview = ({
    cartDatasets,
    loading,
    overlappingDatasetIds,
    selectedDataProductId,
}: CartOverviewProps) => {
    const { t } = useTranslation();
    const dispatch = useAppDispatch();
    const removeFromCart = (datasetId: string) => {
        dispatch(removeDatasetFromCart({ datasetId }));
    };

    return (
        <Card title={<Typography.Title level={3}>Checkout summary</Typography.Title>}>
            <List
                footer={
                    <Flex justify={'flex-end'}>
                        {t('{{count}} output ports', {
                            count: cartDatasets?.length || 0,
                        })}
                    </Flex>
                }
                style={{ width: '100%' }}
                loading={loading}
                dataSource={cartDatasets}
                locale={{ emptyText: t('No output ports in cart, go to the marketplace to add new output ports') }}
                rowKey={(ds) => ds.id}
                renderItem={(dataset) => (
                    <List.Item>
                        <Flex justify="space-between" align="start">
                            <CartOverviewItem
                                dataset={dataset}
                                overlapping={overlappingDatasetIds?.includes(dataset.id)}
                                selectedDataProductId={selectedDataProductId}
                            />
                            <Button
                                type={'text'}
                                icon={<DeleteOutlined />}
                                danger
                                style={{ marginLeft: 'auto' }}
                                onClick={(e) => {
                                    e.preventDefault();
                                    removeFromCart(dataset.id);
                                }}
                            />
                        </Flex>
                    </List.Item>
                )}
            />
        </Card>
    );
};
