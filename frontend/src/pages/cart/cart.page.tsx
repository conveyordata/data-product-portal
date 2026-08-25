import { PlusOutlined, ShopOutlined, ShoppingCartOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { Button, Col, Empty, Flex, Row, Typography } from 'antd';
import posthog from 'posthog-js';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import ExplorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import { CardSelection } from '@/components/card-selection/card-selection.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { CartOverview } from '@/pages/cart/components/cart-overview.component.tsx';
import { ExistingDataProductForm } from '@/pages/cart/components/existing-data-product-form.tsx';
import { ExistingExplorationForm } from '@/pages/cart/components/existing-exploration-form.tsx';
import { NewDataProductForm } from '@/pages/cart/components/new-data-product-form.tsx';
import { NewExplorationForm } from '@/pages/cart/components/new-exploration-form.tsx';
import { useAppDispatch } from '@/store';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import {
    DataProductChoiceOptions,
    ExistingOrNew,
    removeOutputPortFromCart,
    selectCartDataProductTypeChoice,
    selectCartExistingOrNewChoice,
    selectCartOutputPortIds,
    setCartExplorationChoices,
} from '@/store/features/cart/cart-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';

function ExplorationsCart() {
    const { t } = useTranslation();
    const dispatch = useAppDispatch();
    const dataProductTypeChoice = useSelector(selectCartDataProductTypeChoice);
    const existingOrNewChoice = useSelector(selectCartExistingOrNewChoice);
    const clearSelectedIds = useCallback(() => {
        setSelectedDataProductId(undefined);
        setSelectedExplorationId(undefined);
    }, []);

    const setDataProductTypeChoice = useCallback(
        (choice: DataProductChoiceOptions | null) => {
            clearSelectedIds();
            posthog.capture(PosthogEvents.CART_DATA_PRODUCT_OR_EXPLORATION_CHOICE, { choice });
            dispatch(setCartExplorationChoices({ dataProductTypeChoice: choice, existingOrNewChoice: null }));
        },
        [clearSelectedIds, dispatch],
    );
    const setExistingOrNewChoice = useCallback(
        (choice: ExistingOrNew | null) => {
            clearSelectedIds();
            posthog.capture(PosthogEvents.CART_EXISTING_OR_NEW_CHOICE, { choice });
            dispatch(setCartExplorationChoices({ dataProductTypeChoice, existingOrNewChoice: choice }));
        },
        [clearSelectedIds, dispatch, dataProductTypeChoice],
    );
    const [selectedDataProductId, setSelectedDataProductId] = useState<string | undefined>(undefined);
    const [selectedExplorationId, setSelectedExplorationId] = useState<string | undefined>(undefined);
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ShopOutlined /> {t('Marketplace')}
                    </>
                ),
                path: ApplicationPaths.Marketplace,
            },
            {
                title: (
                    <>
                        <ShoppingCartOutlined /> {t('Cart')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);

    const {
        data: { output_ports: outputPorts = [] } = {},
        isFetching: fetchingOutputPorts,
        isSuccess,
    } = useSearchOutputPortsQuery({ limit: 1000 });
    const cartOutputPortIds = useSelector(selectCartOutputPortIds);

    useEffect(() => {
        if (!isSuccess || cartOutputPortIds.length === 0) {
            return;
        }

        const availableOutputPortIds = new Set(outputPorts.map((outputPort) => outputPort.id));
        const staleCartOutputPortIds = cartOutputPortIds.filter(
            (outputPortId) => !availableOutputPortIds.has(outputPortId),
        );

        staleCartOutputPortIds.forEach((outputPortId) => {
            dispatch(removeOutputPortFromCart({ outputPortId }));
        });
    }, [cartOutputPortIds, dispatch, isSuccess, outputPorts]);

    const cartOutputPorts = useMemo(() => {
        if (cartOutputPortIds.length === 0) {
            return [];
        }
        return outputPorts?.filter((outputPort) => cartOutputPortIds.includes(outputPort.id));
    }, [outputPorts, cartOutputPortIds]);
    const form = useMemo(() => {
        if (!dataProductTypeChoice || !existingOrNewChoice) {
            return null;
        }
        if (dataProductTypeChoice === DataProductChoiceOptions.data_product) {
            if (existingOrNewChoice === ExistingOrNew.existing) {
                return <ExistingDataProductForm setSelectedDataProductId={setSelectedDataProductId} />;
            }
            if (existingOrNewChoice === ExistingOrNew.new) {
                return <NewDataProductForm />;
            }
        }
        if (dataProductTypeChoice === DataProductChoiceOptions.exploration) {
            if (existingOrNewChoice === ExistingOrNew.new) {
                return <NewExplorationForm />;
            }
            if (existingOrNewChoice === ExistingOrNew.existing) {
                return <ExistingExplorationForm setSelectedExplorationId={setSelectedExplorationId} />;
            }
        }
        return null;
    }, [dataProductTypeChoice, existingOrNewChoice]);
    if (cartOutputPortIds?.length === 0) {
        return (
            <Empty
                description={
                    <Typography.Text>
                        {t('Your cart is currently empty. Explore the marketplace to add items.')}
                    </Typography.Text>
                }
            >
                <Link to={ApplicationPaths.Marketplace}>
                    <Button type="primary">{t('Marketplace')}</Button>
                </Link>
            </Empty>
        );
    }
    return (
        <Row gutter={16}>
            <Col span={16}>
                <Flex vertical gap="middle">
                    <CardSelection
                        value={dataProductTypeChoice}
                        onChange={setDataProductTypeChoice}
                        options={[
                            {
                                title: t('I want to explore this data'),
                                description: t('I need a one-time answer or personal sandbox'),
                                icon: <ExplorationBorderIcon />,
                                value: DataProductChoiceOptions.exploration,
                            },
                            {
                                title: t('I want to build Data Products'),
                                description: t('I want to transform, govern and share data with others'),
                                icon: (
                                    <CustomSvgIconLoader
                                        iconComponent={getDataProductTypeIcon()}
                                        hasRoundBorder={true}
                                        color={
                                            dataProductTypeChoice === DataProductChoiceOptions.data_product
                                                ? 'primary'
                                                : 'dark'
                                        }
                                    />
                                ),
                                value: DataProductChoiceOptions.data_product,
                            },
                        ]}
                    />
                    {dataProductTypeChoice && (
                        <CardSelection
                            value={existingOrNewChoice}
                            onChange={setExistingOrNewChoice}
                            options={[
                                {
                                    title: t('Create a new {{dataProductChoice}}', {
                                        dataProductChoice:
                                            dataProductTypeChoice === DataProductChoiceOptions.data_product
                                                ? t('Data Product')
                                                : t('Exploration'),
                                    }),
                                    icon: <PlusOutlined />,
                                    value: ExistingOrNew.new,
                                },
                                {
                                    title: t('Select an existing {{dataProductChoice}}', {
                                        dataProductChoice:
                                            dataProductTypeChoice === DataProductChoiceOptions.data_product
                                                ? t('Data Product')
                                                : t('Exploration'),
                                    }),
                                    icon: <UnorderedListOutlined />,
                                    value: ExistingOrNew.existing,
                                },
                            ]}
                        />
                    )}
                    {form}
                </Flex>
            </Col>
            <Col span={8} style={{ position: 'sticky', top: 0, alignSelf: 'flex-start' }}>
                <CartOverview
                    loading={fetchingOutputPorts}
                    cartOutputPorts={cartOutputPorts}
                    selectedDataProductId={selectedDataProductId}
                    selectedExplorationId={selectedExplorationId}
                    dataProductTypeChoice={dataProductTypeChoice}
                />
            </Col>
        </Row>
    );
}

export default ExplorationsCart;
