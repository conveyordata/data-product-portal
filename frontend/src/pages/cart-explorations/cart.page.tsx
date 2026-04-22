import {
    ExperimentOutlined,
    GiftOutlined,
    PlusOutlined,
    ShopOutlined,
    ShoppingCartOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import { Col, Flex, Row } from 'antd';
import { parseAsStringEnum, useQueryState } from 'nuqs';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { CardSelection } from '@/pages/cart-explorations/components/card-selection.tsx';
import { CartOverview } from '@/pages/cart-explorations/components/cart-overview.component.tsx';
import { ExistingDataProductForm } from '@/pages/cart-explorations/components/existing-data-product-form.tsx';
import { NewDataProductForm } from '@/pages/cart-explorations/components/new-data-product-form.tsx';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

export enum DataProductChoiceOptions {
    exploration = 'EXPLORATION',
    data_product = 'DATA_PRODUCT',
}

export enum ExistingOrNew {
    existing = 'EXISTING',
    new = 'new',
}

function ExplorationsCart() {
    const { t } = useTranslation();
    const [dataProductTypeChoice, setDataProductTypeChoice] = useQueryState(
        'data-product-type-choice',
        parseAsStringEnum<DataProductChoiceOptions>(Object.values(DataProductChoiceOptions)),
    );
    const [existingOrNewChoice, setExistingOrNewChoice] = useQueryState(
        'existing-or-new',
        parseAsStringEnum<ExistingOrNew>(Object.values(ExistingOrNew)),
    );
    const [selectedDataProductId, setSelectedDataProductId] = useState<string | undefined>(undefined);
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
                    {dataProductTypeChoice === DataProductChoiceOptions.data_product &&
                        !!existingOrNewChoice &&
                        (existingOrNewChoice === ExistingOrNew.existing ? (
                            <ExistingDataProductForm
                                cartOutputPorts={cartOutputPorts}
                                setSelectedDataProductId={setSelectedDataProductId}
                            />
                        ) : (
                            <NewDataProductForm cartOutputPorts={cartOutputPorts} />
                        ))}
                </Flex>
            </Col>
            <Col span={8}>
                <CartOverview
                    loading={fetchingOutputPorts}
                    cartOutputPorts={cartOutputPorts}
                    selectedDataProductId={selectedDataProductId}
                />
            </Col>
        </Row>
    );
}

export default ExplorationsCart;
