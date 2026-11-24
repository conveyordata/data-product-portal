import Icon, { BarChartOutlined, InfoCircleOutlined, ShareAltOutlined } from '@ant-design/icons';
import {
    Button,
    Card,
    Descriptions,
    type DescriptionsProps,
    Divider,
    Flex,
    Space,
    Tag,
    Tooltip,
    Typography,
    theme,
} from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import { OutputPortOutlined } from '@/components/icons';
import { useAppDispatch } from '@/store';
import type { SearchDataProductsResponseItem } from '@/store/api/services/generated/dataProductsSearchApi.ts';
import {
    addOutputPortToCart,
    removeOutputPortFromCart,
    selectCartOutputPortIds,
} from '@/store/features/cart/cart-slice.ts';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import styles from './data-product-marketplace-card-layout.module.scss';
import { SelectOutputPortsModal } from './select-output-ports-modal.component';

const TOOLTIP_OUTPUT_PORT_LIMIT = 3;

type Props = {
    dataProduct: SearchDataProductsResponseItem;
};

export function DataProductMarketplaceCard({ dataProduct }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const dispatch = useAppDispatch();
    const cartOutputPortIds = useSelector(selectCartOutputPortIds);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const outputPorts = dataProduct.output_ports;
    const inCartCount = outputPorts.filter((port) => cartOutputPortIds.includes(port.id)).length;
    const isInCart = outputPorts.length > 0 && inCartCount === outputPorts.length;
    let cartLabel = t('Add to cart');
    if (isInCart) {
        cartLabel = t('In cart');
    } else if (inCartCount > 0) {
        cartLabel = t('{{count}} of {{total}} in cart', { count: inCartCount, total: outputPorts.length });
    }

    const shop = () => {
        if (!addsDirectlyToCart(dataProduct)) {
            setIsModalOpen(true);
            return;
        }
        const [outputPort] = outputPorts;
        if (isInCart) {
            dispatch(removeOutputPortFromCart({ outputPortId: outputPort.id }));
        } else {
            dispatch(
                addOutputPortToCart({ outputPortId: outputPort.id, accessModeId: outputPort.access_modes[0]?.id }),
            );
        }
    };

    const details: DescriptionsProps['items'] = [
        {
            key: 'domain',
            label: (
                <Space>
                    <ShareAltOutlined />
                    {t('Domain')}
                </Space>
            ),
            children: <Typography.Text ellipsis={{ tooltip: true }}>{dataProduct.domain.name}</Typography.Text>,
        },
        {
            key: 'type',
            label: (
                <Space>
                    <Icon component={getDataProductTypeIcon(dataProduct.type.icon_key)} />
                    {t('Type')}
                </Space>
            ),
            children: <Typography.Text ellipsis={{ tooltip: true }}>{dataProduct.type.name}</Typography.Text>,
        },
        {
            key: 'output ports',
            label: (
                <Space>
                    <OutputPortOutlined />
                    {t('Output Ports')}
                </Space>
            ),
            children: (
                <Tooltip
                    title={
                        outputPorts.length > 0 && (
                            <Flex vertical gap="small">
                                {outputPorts.slice(0, TOOLTIP_OUTPUT_PORT_LIMIT).map((port) => (
                                    <div key={port.id}>
                                        <strong>{port.name}</strong>
                                        <div>{port.description}</div>
                                    </div>
                                ))}
                                {outputPorts.length > TOOLTIP_OUTPUT_PORT_LIMIT &&
                                    t('+{{count}} more Output Ports', {
                                        count: outputPorts.length - TOOLTIP_OUTPUT_PORT_LIMIT,
                                    })}
                            </Flex>
                        )
                    }
                >
                    <Space size="small">
                        {outputPorts.length}
                        {outputPorts.length > 0 && <InfoCircleOutlined />}
                    </Space>
                </Tooltip>
            ),
        },
        {
            key: 'usage',
            label: (
                <Space>
                    <BarChartOutlined />
                    {t('Usage')}
                </Space>
            ),
            children: (
                <Typography.Text ellipsis={{ tooltip: true }}>
                    {t('{{count}} consumers', { count: dataProduct.consumer_count })}
                </Typography.Text>
            ),
        },
    ];

    return (
        <>
            <Card
                data-cy="data-product-card"
                variant="borderless"
                // Subgrid rows (title, description, details) come from the marketplace grid to align cards per row
                styles={{
                    root: {
                        display: 'grid',
                        gridRow: 'span 3',
                        gridTemplateRows: 'subgrid',
                        rowGap: 0,
                    },
                    body: {
                        display: 'grid',
                        gridRow: 'span 3',
                        gridTemplateRows: 'subgrid',
                        rowGap: token.paddingXXS,
                        padding: token.padding,
                    },
                }}
            >
                <Flex vertical justify="space-between">
                    <Flex justify="space-between" align="start" gap="small">
                        <Link to={createDataProductIdPath(dataProduct.id)}>
                            <Typography.Title
                                level={5}
                                ellipsis={{ rows: 2, tooltip: true }}
                                style={{ marginBottom: 0 }}
                            >
                                {dataProduct.name}
                            </Typography.Title>
                        </Link>
                        <Tooltip
                            title={
                                outputPorts.length === 0 && t('This Data Product has no Output Ports you can request')
                            }
                        >
                            <Button
                                size="small"
                                color={isInCart ? 'green' : 'primary'}
                                variant="solid"
                                disabled={outputPorts.length === 0}
                                onClick={shop}
                            >
                                {cartLabel}
                            </Button>
                        </Tooltip>
                    </Flex>
                    <Divider style={{ margin: `${token.marginXS}px 0 0` }} />
                </Flex>
                <Flex vertical gap="small">
                    <Typography.Paragraph ellipsis={{ rows: 2, tooltip: true }} style={{ marginBottom: 0 }}>
                        {dataProduct.description || t('No description available.')}
                    </Typography.Paragraph>
                    {dataProduct.tags.length > 0 && (
                        <Space size="small" wrap>
                            {dataProduct.tags.map((tag) => (
                                <Tag color="success" key={tag.id}>
                                    {tag.value}
                                </Tag>
                            ))}
                        </Space>
                    )}
                </Flex>
                <Descriptions
                    layout="vertical"
                    size="small"
                    colon={false}
                    column={2}
                    className={styles.cardDetails}
                    style={{ marginTop: token.marginSM }}
                    items={details}
                />
            </Card>
            {isModalOpen && <SelectOutputPortsModal dataProduct={dataProduct} onClose={() => setIsModalOpen(false)} />}
        </>
    );
}

function addsDirectlyToCart(dataProduct: SearchDataProductsResponseItem): boolean {
    return dataProduct.output_ports.length === 1 && dataProduct.output_ports[0].access_modes.length <= 1;
}
