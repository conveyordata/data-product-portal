import {
    ExperimentOutlined,
    GiftOutlined,
    PlusOutlined,
    ShopOutlined,
    ShoppingCartOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import { Col, Flex, Row } from 'antd';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { CardSelection } from '@/pages/cart-explorations/components/card-selection.tsx';
import { CartOverview } from '@/pages/cart-explorations/components/cart-overview.component.tsx';
import { ExistingDataProductForm } from '@/pages/cart-explorations/components/existing-data-product-form.tsx';
import { ExistingExplorationForm } from '@/pages/cart-explorations/components/existing-exploration-form.tsx';
import { NewDataProductForm } from '@/pages/cart-explorations/components/new-data-product-form.tsx';
import { NewExplorationForm } from '@/pages/cart-explorations/components/new-exploration-form.tsx';
import { useAppDispatch } from '@/store';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import {
    DataProductChoiceOptions,
    ExistingOrNew,
    selectCartDataProductTypeChoice,
    selectCartDatasetIds,
    selectCartExistingOrNewChoice,
    setCartExplorationChoices,
} from '@/store/features/cart/cart-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

function ExplorationsCart() {
    const { t } = useTranslation();
    const dispatch = useAppDispatch();
    const dataProductTypeChoice = useSelector(selectCartDataProductTypeChoice);
    const existingOrNewChoice = useSelector(selectCartExistingOrNewChoice);

    const setDataProductTypeChoice = useCallback(
        (choice: DataProductChoiceOptions | null) => {
            dispatch(setCartExplorationChoices({ dataProductTypeChoice: choice, existingOrNewChoice: null }));
        },
        [dispatch],
    );
    const setExistingOrNewChoice = useCallback(
        (choice: ExistingOrNew | null) => {
            dispatch(setCartExplorationChoices({ dataProductTypeChoice, existingOrNewChoice: choice }));
        },
        [dispatch, dataProductTypeChoice],
    );
    const [selectedDataProductId, setSelectedDataProductId] = useState<string | undefined>(undefined);
    const [selectedExplorationId, setSelectedExplorationId] = useState<string | undefined>(undefined);
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        {' '}
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

    const { data: { output_ports: outputPorts = [] } = {}, isFetching: fetchingOutputPorts } =
        useSearchOutputPortsQuery({ limit: 1000 });
    const cartDatasetIds = useSelector(selectCartDatasetIds);
    const cartOutputPorts = useMemo(() => {
        if (cartDatasetIds.length === 0) {
            return [];
        }
        return outputPorts?.filter((dataset) => cartDatasetIds.includes(dataset.id));
    }, [outputPorts, cartDatasetIds]);
    const form = useMemo(() => {
        if (!dataProductTypeChoice || !existingOrNewChoice) {
            return null;
        }
        if (dataProductTypeChoice === DataProductChoiceOptions.data_product) {
            if (existingOrNewChoice === ExistingOrNew.existing) {
                return (
                    <ExistingDataProductForm
                        cartOutputPorts={cartOutputPorts}
                        setSelectedDataProductId={setSelectedDataProductId}
                    />
                );
            }
            if (existingOrNewChoice === ExistingOrNew.new) {
                return <NewDataProductForm cartOutputPorts={cartOutputPorts} />;
            }
        }
        if (dataProductTypeChoice === DataProductChoiceOptions.exploration) {
            if (existingOrNewChoice === ExistingOrNew.new) {
                return <NewExplorationForm cartOutputPorts={cartOutputPorts} />;
            }
            if (existingOrNewChoice === ExistingOrNew.existing) {
                return (
                    <ExistingExplorationForm
                        cartOutputPorts={cartOutputPorts}
                        setSelectedExplorationId={setSelectedExplorationId}
                    />
                );
            }
        }
        return null;
    }, [dataProductTypeChoice, existingOrNewChoice, cartOutputPorts]);
    return (
        <Row gutter={16}>
            <Col span={16}>
                <Flex vertical gap={'middle'}>
                    <CardSelection
                        selectedChoice={dataProductTypeChoice}
                        setSelectedChoice={setDataProductTypeChoice}
                        options={[
                            {
                                title: t('I want to explore this data'),
                                description: t('I need a one-time answer or personal sandbox'),
                                icon: ExperimentOutlined,
                                value: DataProductChoiceOptions.exploration,
                            },
                            {
                                title: t('I want to build Data Products'),
                                description: t('I want to transform, govern and share data with others'),
                                icon: GiftOutlined,
                                value: DataProductChoiceOptions.data_product,
                            },
                        ]}
                    />
                    {dataProductTypeChoice && (
                        <CardSelection
                            selectedChoice={existingOrNewChoice}
                            setSelectedChoice={setExistingOrNewChoice}
                            options={[
                                {
                                    title: t('Create a new {{dataProductChoice}}', {
                                        dataProductChoice:
                                            dataProductTypeChoice === DataProductChoiceOptions.data_product
                                                ? t('Data Product')
                                                : t('Exploration'),
                                    }),
                                    icon: PlusOutlined,
                                    value: ExistingOrNew.new,
                                },
                                {
                                    title: t('Select an existing {{dataProductChoice}}', {
                                        dataProductChoice:
                                            dataProductTypeChoice === DataProductChoiceOptions.data_product
                                                ? t('Data Product')
                                                : t('Exploration'),
                                    }),
                                    icon: UnorderedListOutlined,
                                    value: ExistingOrNew.existing,
                                },
                            ]}
                        />
                    )}
                    {form}
                </Flex>
            </Col>
            <Col span={8}>
                <CartOverview
                    loading={fetchingOutputPorts}
                    cartOutputPorts={cartOutputPorts}
                    selectedDataProductId={selectedDataProductId}
                    selectedExplorationId={selectedExplorationId}
                />
            </Col>
        </Row>
    );
}

export default ExplorationsCart;
