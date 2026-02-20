import {
    BellOutlined,
    CheckCircleOutlined,
    MessageOutlined,
    PlusOutlined,
    ShopOutlined,
    ShoppingCartOutlined,
} from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import {
    Alert,
    Button,
    Card,
    Col,
    Divider,
    Flex,
    Form,
    type FormProps,
    Row,
    Select,
    Skeleton,
    Typography,
    theme,
} from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { parseAsString, useQueryState } from 'nuqs';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { CartOverview } from '@/pages/cart/components/cart-overview.component.tsx';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    useGetDataProductInputPortsQuery,
    useGetDataProductQuery,
    useGetDataProductsQuery,
    useLinkInputPortsToDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetDataProductOutputPortsQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { clearCart, selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';

const cartFormDataStorageKey = 'cart-form-data';

function Cart() {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const [createdProductId] = useQueryState('createdProductId', parseAsString.withDefault(''));
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
    const [requestDatasetAccessForDataProduct, { isSuccess: requestingAccessSuccess, isLoading: isRequestingAccess }] =
        useLinkInputPortsToDataProductMutation();
    const cartDatasetIds = useSelector(selectCartDatasetIds);
    const cartOutputPorts = useMemo(() => {
        if (cartDatasetIds.length === 0) {
            return [];
        }
        return outputPorts?.filter((dataset) => cartDatasetIds.includes(dataset.id));
    }, [outputPorts, cartDatasetIds]);

    const currentUser = useSelector(selectCurrentUser);
    const { data: { data_products: userDataProducts = [] } = {}, isFetching: isFetchingUserDataProducts } =
        useGetDataProductsQuery(currentUser?.id, {
            skip: currentUser === null || !currentUser?.id,
        });
    const [form] = Form.useForm<CartFormData>();

    type CartFormData = {
        dataProductId?: string;
        justification?: string;
    };
    const initialValues: CartFormData | undefined = useMemo(() => {
        let data: CartFormData = {};
        if (isFetchingUserDataProducts) {
            return undefined;
        }
        const savedData = localStorage.getItem(cartFormDataStorageKey);
        if (savedData) {
            data = JSON.parse(savedData) as CartFormData;
        }
        if (createdProductId !== '') {
            data.dataProductId = createdProductId;
        }
        if (data.dataProductId && !userDataProducts.map((dataProduct) => dataProduct.id).includes(data.dataProductId)) {
            data.dataProductId = undefined;
        }
        return data;
    }, [createdProductId, userDataProducts, isFetchingUserDataProducts]);

    const onFinish: FormProps<CartFormData>['onFinish'] = (values) => {
        if (
            !values.justification ||
            !values.dataProductId ||
            cartOutputPorts === undefined ||
            cartOutputPorts.length === 0
        ) {
            return;
        }
        posthog.capture(PosthogEvents.CART_CHECKOUT_COMPLETED, {
            cartSize: cartOutputPorts?.length,
        });
        requestDatasetAccessForDataProduct({
            id: values.dataProductId,
            linkInputPortsToDataProduct: {
                input_ports: cartOutputPorts?.map((dataset) => dataset.id),
                justification: values.justification,
            },
        });
    };
    const onValuesChange: FormProps<CartFormData>['onValuesChange'] = (_, values: CartFormData) => {
        localStorage.setItem(cartFormDataStorageKey, JSON.stringify(values));
    };
    const dataProductOptions =
        userDataProducts?.map((dataProduct) => {
            return {
                value: dataProduct?.id,
                label: dataProduct?.name,
            };
        }) ?? [];
    const selectedDataProductId = Form.useWatch('dataProductId', form);
    const createNewDataProduct = () => {
        posthog.capture(PosthogEvents.CART_CREATE_DATA_PRODUCT);
        navigate({
            pathname: ApplicationPaths.DataProductNew,
            search: new URLSearchParams({ fromMarketplace: 'true' }).toString(),
        });
    };

    const { data: selectedDataProduct, refetch: refetchSelectedDataProduct } = useGetDataProductQuery(
        selectedDataProductId ?? '',
        {
            skip: !selectedDataProductId || isFetchingUserDataProducts || userDataProducts === undefined,
        },
    );
    const { data: { input_ports: inputPorts = [] } = {} } = useGetDataProductInputPortsQuery(
        selectedDataProductId ?? '',
        {
            skip: !selectedDataProductId || isFetchingUserDataProducts || userDataProducts === undefined,
        },
    );
    const { data: { output_ports: selectedDataProductOutputPorts = [] } = {} } = useGetDataProductOutputPortsQuery(
        selectedDataProductId ?? '',
        {
            skip: !selectedDataProductId || isFetchingUserDataProducts || userDataProducts === undefined,
        },
    );
    useEffect(() => {
        if (!selectedDataProduct) {
            return;
        }
        if (selectedDataProduct.id !== selectedDataProductId) {
            refetchSelectedDataProduct();
        }
    });

    const overlappingOutputPortIds = useMemo(() => {
        return inputPorts
            .filter((link) => cartDatasetIds.includes(link.output_port_id))
            .map((link) => link.output_port_id);
    }, [cartDatasetIds, inputPorts]);

    const selectedProductOutputPortsInCart = useMemo(() => {
        return selectedDataProductOutputPorts.filter((ds) => cartDatasetIds.includes(ds.id));
    }, [selectedDataProductOutputPorts, cartDatasetIds]);

    useEffect(() => {
        if (requestingAccessSuccess && selectedDataProductId) {
            dispatch(clearCart());
            localStorage.removeItem(cartFormDataStorageKey);
            dispatchMessage({ content: t('Your requests have successfully been created.'), type: 'success' });

            navigate(createDataProductIdPath(selectedDataProductId, DataProductTabKeys.InputPorts));
        }
    }, [requestingAccessSuccess, selectedDataProductId, dispatch, navigate, t]);

    const submitFormIssues = useMemo(() => {
        const submitFormIssues = [];
        if (overlappingOutputPortIds.length > 0) {
            submitFormIssues.push({
                key: 'overlappingOutputPortId',
                value: t(
                    'There are currently {{count}} Output Ports in the cart, for which the selected Data Product already has access, or has an access request.',
                    {
                        count: overlappingOutputPortIds.length,
                    },
                ),
            });
        }
        if (selectedProductOutputPortsInCart.length > 0) {
            submitFormIssues.push({
                key: 'selectedProductOutputPortsInCart',
                value: t(
                    'There are currently {{count}} Output Ports, that are part of your selected Data Product, please remove them.',
                    {
                        count: selectedProductOutputPortsInCart.length,
                    },
                ),
            });
        }

        return submitFormIssues;
    }, [overlappingOutputPortIds, selectedProductOutputPortsInCart, t]);
    return (
        <Row gutter={16}>
            <Col span={10}>
                <CartOverview
                    loading={fetchingOutputPorts}
                    cartOutputPorts={cartOutputPorts}
                    overlappingDatasetIds={overlappingOutputPortIds}
                    selectedDataProductId={selectedDataProductId}
                />
            </Col>
            <Col span={14}>
                <Card title={<Typography.Title level={3}>{t('Data checkout')}</Typography.Title>}>
                    {initialValues === undefined ? (
                        <Skeleton />
                    ) : (
                        <Form<CartFormData>
                            key={initialValues.dataProductId}
                            layout={'vertical'}
                            onFinish={onFinish}
                            form={form}
                            onValuesChange={onValuesChange}
                            initialValues={initialValues}
                        >
                            <Form.Item<CartFormData>
                                name="dataProductId"
                                label={t('Data Product')}
                                rules={[{ required: true, message: t('Please select a Data Product') }]}
                            >
                                <Select
                                    placeholder={t('Select a Data Product')}
                                    options={dataProductOptions}
                                    loading={isFetchingUserDataProducts}
                                    showSearch={{
                                        filterOption: (input, option) =>
                                            (option?.label ?? '').toLowerCase().includes(input.toLowerCase()),
                                    }}
                                    popupRender={(menu) => (
                                        <>
                                            <Button
                                                type="text"
                                                icon={<PlusOutlined />}
                                                style={{ width: '100%' }}
                                                onClick={createNewDataProduct}
                                            >
                                                {t('Create new Data Product')}
                                            </Button>
                                            <Divider style={{ margin: '8px 0' }} />
                                            {menu}
                                        </>
                                    )}
                                />
                            </Form.Item>
                            {submitFormIssues.length > 0 && (
                                <Alert
                                    title={t('Cannot submit request')}
                                    description={
                                        <ul style={{ margin: 0, paddingLeft: 20 }}>
                                            {submitFormIssues.map((reason) => (
                                                <li key={reason.key}>{reason.value}</li>
                                            ))}
                                        </ul>
                                    }
                                    type="warning"
                                    showIcon
                                    style={{ marginBottom: 16 }}
                                />
                            )}
                            <Form.Item<CartFormData>
                                name="justification"
                                label={'Business justification'}
                                rules={[
                                    {
                                        required: true,
                                        message: t('Please explain why you need access to these Output Ports'),
                                    },
                                ]}
                            >
                                <TextArea rows={4} placeholder="Explain why you need access to these Output Ports" />
                            </Form.Item>
                            <Form.Item label={null}>
                                <Flex gap={'small'}>
                                    <Link to={ApplicationPaths.Marketplace} style={{ width: '100%' }}>
                                        <Button type="default" style={{ width: '100%' }}>
                                            {t('Continue browsing')}
                                        </Button>
                                    </Link>
                                    <Button
                                        type="primary"
                                        htmlType="submit"
                                        style={{ width: '100%' }}
                                        loading={isRequestingAccess}
                                        disabled={
                                            fetchingOutputPorts ||
                                            submitFormIssues.length > 0 ||
                                            cartOutputPorts === undefined ||
                                            cartOutputPorts?.length === 0
                                        }
                                    >
                                        {t('Submit access requests')}
                                    </Button>
                                </Flex>
                            </Form.Item>
                        </Form>
                    )}
                    <Divider />
                    <Flex vertical>
                        <Typography.Text>
                            <CheckCircleOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('Owners typically respond within 24-48 hours')}
                        </Typography.Text>
                        <Typography.Text>
                            <BellOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('You will get notified when access is granted or denied')}
                        </Typography.Text>
                        <Typography.Text>
                            <MessageOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('Message owners directly for questions')}
                        </Typography.Text>
                    </Flex>
                </Card>
            </Col>
        </Row>
    );
}

export default Cart;
