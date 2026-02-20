import { DeleteOutlined, WarningOutlined } from '@ant-design/icons';
import { Button, Card, Descriptions, Flex, List, Space, Tag, Tooltip, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useAppDispatch } from '@/store';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { removeDatasetFromCart } from '@/store/features/cart/cart-slice.ts';
import { createDataProductIdPath, createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { useGetDataProductOwners } from '@/utils/data-product-user-role.helper.ts';

type CartOverviewItemProps = {
    outputPort: SearchOutputPortsResponseItem;
    overlapping?: boolean;
    selectedDataProductId?: string;
};

function CartOverviewItem({ outputPort, overlapping, selectedDataProductId }: CartOverviewItemProps) {
    const { t } = useTranslation();
    const dataProductOwners = useGetDataProductOwners(outputPort.data_product_id);

    const warningTooltip = useMemo(() => {
        if (selectedDataProductId === outputPort.data_product_id) {
            return t('You can not request access to your own Output Ports');
        }
        if (overlapping) {
            return t('The selected Data Product already has access, or an access request open for this Output Port');
        }
        return null;
    }, [selectedDataProductId, outputPort.data_product_id, overlapping, t]);

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
                        <Link
                            to={createMarketplaceOutputPortPath(outputPort.id, outputPort.data_product_id)}
                            target={'_blank'}
                        >
                            <Typography.Text>{outputPort.name}</Typography.Text>
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
                    label: <Typography.Text strong>{t('Data Product')}</Typography.Text>,
                    children: (
                        <Link to={createDataProductIdPath(outputPort.data_product_id)} target={'_blank'}>
                            <Typography.Text>{outputPort.data_product_name}</Typography.Text>
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
    cartOutputPorts?: SearchOutputPortsResponseItem[];
    overlappingDatasetIds?: string[];
    loading?: boolean;
    selectedDataProductId?: string;
};

export const CartOverview = ({
    cartOutputPorts,
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
                        {t('{{ count }} Output Ports', {
                            count: cartOutputPorts?.length || 0,
                        })}
                    </Flex>
                }
                style={{ width: '100%' }}
                loading={loading}
                dataSource={cartOutputPorts}
                locale={{ emptyText: t('No Output Ports in cart, go to the marketplace to add new Output Ports') }}
                rowKey={(ds) => ds.id}
                renderItem={(dataset) => (
                    <List.Item>
                        <Flex justify="space-between" align="start">
                            <CartOverviewItem
                                outputPort={dataset}
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
