import { DeleteOutlined, WarningTwoTone } from '@ant-design/icons';
import { Button, Card, Collapse, Descriptions, Flex, Skeleton, Space, Tag, Tooltip, Typography, theme } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { useCartOverlapCheck } from '@/pages/cart/hooks/use-cart-overlap-check.ts';
import { useAppDispatch } from '@/store';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { type DataProductChoiceOptions, removeDatasetFromCart } from '@/store/features/cart/cart-slice.ts';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { useGetDataProductOwners } from '@/utils/data-product-user-role.helper.ts';
import { OutputPortAccessDuration } from './output-port-access-duration';

type CartOverviewItemProps = {
    outputPort: SearchOutputPortsResponseItem;
};

function CartOverviewItem({ outputPort }: CartOverviewItemProps) {
    const { t } = useTranslation();
    const dataProductOwners = useGetDataProductOwners(outputPort.data_product_id);

    const renderOwners = () => {
        if (!dataProductOwners || dataProductOwners.length === 0)
            return <Typography.Text>{t('There are no owners')}</Typography.Text>;

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

type CartOverviewWarningProps = {
    outputPort: SearchOutputPortsResponseItem;
    overlapping?: boolean;
    selectedDataProductId?: string;
};
const CartOverviewWarning = ({ outputPort, overlapping, selectedDataProductId }: CartOverviewWarningProps) => {
    const { token } = theme.useToken();
    const { t } = useTranslation();

    const warningTooltip = useMemo(() => {
        if (selectedDataProductId === outputPort.data_product_id) {
            return t('You can not request access to your own Output Ports');
        }
        if (overlapping) {
            return t('The selected Data Product already has access, or an access request open for this Output Port');
        }
        return null;
    }, [selectedDataProductId, outputPort.data_product_id, overlapping, t]);
    if (warningTooltip === null) {
        return null;
    }
    return (
        <Tooltip title={warningTooltip}>
            <WarningTwoTone twoToneColor={token.colorWarning} />
        </Tooltip>
    );
};

type CartOverviewProps = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
    loading?: boolean;
    selectedDataProductId?: string;
    selectedExplorationId?: string;
    dataProductTypeChoice: DataProductChoiceOptions | null;
};

export const CartOverview = ({
    cartOutputPorts,
    loading,
    selectedDataProductId,
    selectedExplorationId,
    dataProductTypeChoice,
}: CartOverviewProps) => {
    const { t } = useTranslation();
    const dispatch = useAppDispatch();
    const removeFromCart = (datasetId: string) => {
        dispatch(removeDatasetFromCart({ datasetId }));
    };
    const { overlappingOutputPortIds } = useCartOverlapCheck({ selectedDataProductId, selectedExplorationId });

    return (
        <Card title={<Typography.Title level={3}>{t('Cart summary')}</Typography.Title>}>
            {loading ? (
                <Skeleton active />
            ) : (
                <Collapse
                    accordion
                    items={cartOutputPorts?.map((outputPort) => {
                        return {
                            label: (
                                <Flex vertical gap="small">
                                    <Typography.Text>{outputPort.name}</Typography.Text>
                                    {dataProductTypeChoice && (
                                        <OutputPortAccessDuration
                                            outputPort={outputPort}
                                            dataProductTypeChoice={dataProductTypeChoice}
                                        />
                                    )}
                                </Flex>
                            ),
                            styles: { header: { alignItems: 'center' } },
                            children: <CartOverviewItem outputPort={outputPort} />,
                            extra: (
                                <Space size={'small'} align={'center'}>
                                    <CartOverviewWarning
                                        outputPort={outputPort}
                                        overlapping={overlappingOutputPortIds?.includes(outputPort.id)}
                                        selectedDataProductId={selectedDataProductId}
                                    />
                                    <Button
                                        type={'text'}
                                        icon={<DeleteOutlined />}
                                        danger
                                        size={'small'}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            removeFromCart(outputPort.id);
                                        }}
                                    />
                                </Space>
                            ),
                        };
                    })}
                />
            )}
        </Card>
    );
};
