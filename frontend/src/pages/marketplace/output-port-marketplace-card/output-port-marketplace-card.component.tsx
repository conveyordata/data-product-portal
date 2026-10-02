import {
    BarChartOutlined,
    CheckOutlined,
    DatabaseOutlined,
    EyeOutlined,
    NumberOutlined,
    PlusOutlined,
    ShareAltOutlined,
    ShoppingCartOutlined,
    TeamOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import {
    Button,
    Card,
    ConfigProvider,
    Descriptions,
    type DescriptionsProps,
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
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import SelectAccessModeModal from '@/pages/marketplace/output-port-marketplace-card/select-access-mode-modal.component.tsx';
import { useAppDispatch } from '@/store';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import {
    addOutputPortToCart,
    removeOutputPortFromCart,
    selectCartOutputPortIds,
} from '@/store/features/cart/cart-slice.ts';
import { createDataProductIdPath, createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { OutputPortCardTooltip } from './output-port-card-tooltip.component';
import styles from './output-port-marketplace-card-layout.module.scss';

type Props = {
    outputPort: SearchOutputPortsResponseItem;
};

export function OutputPortMarketplaceCard({ outputPort }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const dispatch = useAppDispatch();
    const cartOutputPortIds = useSelector(selectCartOutputPortIds);

    const [selectAccessModesOutputPort, setSelectAccessModesOutputPort] = useState<
        SearchOutputPortsResponseItem | undefined
    >(undefined);

    const toggleCart = (outputPort: SearchOutputPortsResponseItem) => {
        if (cartOutputPortIds.includes(outputPort.id)) {
            dispatch(removeOutputPortFromCart({ outputPortId: outputPort.id }));
        } else {
            if (outputPort.access_modes?.length > 0) {
                setSelectAccessModesOutputPort(outputPort);
            } else {
                dispatch(addOutputPortToCart({ outputPortId: outputPort.id }));
            }
        }
    };

    function createCardDetails(outputPort: SearchOutputPortsResponseItem) {
        const items: DescriptionsProps['items'] = [
            {
                key: 'domain',
                label: (
                    <Space>
                        <ShareAltOutlined />
                        {t('Domain')}
                    </Space>
                ),
                children: <Typography.Text ellipsis={{ tooltip: true }}>{outputPort.domain.name}</Typography.Text>,
            },
            {
                key: 'access type',
                label: (
                    <Space>
                        <DatabaseOutlined />
                        {t('Access type')}
                    </Space>
                ),
                children: <Typography.Text ellipsis={{ tooltip: true }}>{outputPort.access_type}</Typography.Text>,
            },
            {
                key: 'technical assets',
                label: (
                    <Space>
                        <NumberOutlined />
                        {t('Technical Assets')}
                    </Space>
                ),
                children: outputPort.technical_assets_count,
            },
            {
                key: 'data product',
                label: (
                    <Space>
                        <TeamOutlined />
                        {t('Data Product')}
                    </Space>
                ),
                children: (
                    <Typography.Paragraph ellipsis={{ rows: 2, tooltip: true }}>
                        <Link to={createDataProductIdPath(outputPort.data_product_id)}>
                            {outputPort.data_product_name}
                        </Link>
                    </Typography.Paragraph>
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
                    <OutputPortCardTooltip
                        outputPortId={outputPort.id}
                        dataProductId={outputPort.data_product_id}
                        number_of_consumers={outputPort.abstract_data_product_count}
                    />
                ),
            },
        ];
        return items;
    }

    if (!outputPort) return <LoadingSpinner />;
    return (
        <ConfigProvider
            theme={{
                components: {
                    Card: {
                        actionsLiMargin: `${token.paddingXS}px 0`,
                        colorBorderSecondary: token.colorBorder,
                    },
                },
            }}
        >
            <Card
                key={outputPort.id}
                data-cy="output-port-card"
                // Subgrid rows (title, description, details, actions) come from the marketplace grid to align cards per row
                styles={{
                    root: { display: 'grid', gridRow: 'span 4', gridTemplateRows: 'subgrid', rowGap: 0 },
                    body: {
                        display: 'grid',
                        gridRow: 'span 3',
                        gridTemplateRows: 'subgrid',
                        rowGap: token.paddingXXS,
                        padding: 12,
                    },
                }}
                actions={[
                    <Tooltip key="details" title={t('View details')}>
                        <Link to={createMarketplaceOutputPortPath(outputPort.id, outputPort.data_product_id)}>
                            <Button type="text" icon={<UnorderedListOutlined />} />
                        </Link>
                    </Tooltip>,
                    <Tooltip
                        key="cart"
                        title={cartOutputPortIds.includes(outputPort.id) ? t('Remove from cart') : t('Add to cart')}
                    >
                        <Button
                            key="add to cart"
                            data-cy="add-to-cart"
                            type="text"
                            size="middle"
                            onClick={(e) => {
                                e.preventDefault();
                                toggleCart(outputPort);
                            }}
                        >
                            {cartOutputPortIds.includes(outputPort.id) ? (
                                <>
                                    <CustomSvgIconLoader
                                        size="small"
                                        iconComponent={ShoppingCartOutlined}
                                        color="success"
                                    />
                                    <CustomSvgIconLoader size="small" iconComponent={CheckOutlined} color="success" />
                                </>
                            ) : (
                                <>
                                    <CustomSvgIconLoader
                                        size="small"
                                        iconComponent={ShoppingCartOutlined}
                                        color="primary"
                                    />
                                    <CustomSvgIconLoader size="small" iconComponent={PlusOutlined} color="primary" />
                                </>
                            )}
                        </Button>
                    </Tooltip>,
                ]}
            >
                <Link to={createMarketplaceOutputPortPath(outputPort.id, outputPort.data_product_id)}>
                    <Typography.Title level={5} ellipsis={{ rows: 2, tooltip: true }} style={{ marginBottom: 0 }}>
                        {outputPort.name}
                    </Typography.Title>
                </Link>
                <Flex vertical gap="small">
                    <Typography.Paragraph ellipsis={{ rows: 2, tooltip: true }} style={{ marginBottom: 0 }}>
                        {outputPort.description || 'No description available.'}
                    </Typography.Paragraph>
                    {outputPort.tags?.length > 0 && (
                        <Space size="small" wrap>
                            {outputPort.tags.map((tag) => (
                                <Tag color="success" key={tag.value}>
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
                    items={createCardDetails(outputPort)}
                />
            </Card>
            {selectAccessModesOutputPort !== undefined && (
                <SelectAccessModeModal
                    outputPort={selectAccessModesOutputPort}
                    onClose={() => setSelectAccessModesOutputPort(undefined)}
                    selectAccessMode={(accessMode) => {
                        dispatch(addOutputPortToCart({ outputPortId: outputPort.id, accessModeId: accessMode.id }));
                        setSelectAccessModesOutputPort(undefined);
                    }}
                />
            )}
        </ConfigProvider>
    );
}
