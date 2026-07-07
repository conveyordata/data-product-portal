import { usePostHog } from '@posthog/react';
import { Button, Form, type FormProps, Select, Space, Typography } from 'antd';
import { t } from 'i18next';
import { useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useFormPersist } from '@/hooks/use-form-persist.tsx';
import { FormItemAccessDuration } from '@/pages/cart/components/form-item-access-duration.tsx';
import { FormIssues } from '@/pages/cart/components/form-item-issues.tsx';
import { JustificationFormItem } from '@/pages/cart/components/form-item-justification.tsx';
import { useCartOverlapCheck } from '@/pages/cart/hooks/use-cart-overlap-check.ts';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    useGetDataProductsQuery,
    useRequestInputPortsForDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { clearCart, DataProductChoiceOptions } from '@/store/features/cart/cart-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { createDataProductIdPath } from '@/types/navigation.ts';

type CartFormData = {
    dataProductId?: string;
    justification?: string;
};

type Props = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
    setSelectedDataProductId: (id?: string) => void;
};

export const ExistingDataProductForm = ({ cartOutputPorts, setSelectedDataProductId }: Props) => {
    const dispatch = useAppDispatch();
    const posthog = usePostHog();
    const navigate = useNavigate();

    const [requestInputPortsForDataProduct, { isSuccess: requestingAccessSuccess, isLoading: isRequestingAccess }] =
        useRequestInputPortsForDataProductMutation();
    const [form] = Form.useForm<CartFormData>();
    const selectedDataProductId = Form.useWatch('dataProductId', form);
    useEffect(() => {
        setSelectedDataProductId(selectedDataProductId);
        return () => {
            setSelectedDataProductId(undefined);
        };
    }, [selectedDataProductId, setSelectedDataProductId]);
    const { onValuesChange, clearStorage, isRestored } = useFormPersist<CartFormData>(
        form,
        'cart-existing-data-product-form',
    );

    const { overlappingOutputPortIds, selectedProductOutputPortsInCartIds } = useCartOverlapCheck({
        selectedDataProductId,
    });

    useEffect(() => {
        if (requestingAccessSuccess && selectedDataProductId) {
            dispatch(clearCart());
            dispatchMessage({ content: t('Your requests have successfully been created.'), type: 'success' });

            navigate(createDataProductIdPath(selectedDataProductId, DataProductTabKeys.InputPorts));
        }
    }, [requestingAccessSuccess, selectedDataProductId, dispatch, navigate]);
    const submitFormIssues = useMemo(() => {
        const submitFormIssues = [];
        if (overlappingOutputPortIds.length > 0) {
            submitFormIssues.push({
                key: 'overlappingOutputPortId',
                value: t(
                    'There are currently {{count}} Output Ports in the cart, for which the selected Data Product already has access, or has an access request. Please remove them from the cart before proceeding.',
                    {
                        count: overlappingOutputPortIds.length,
                    },
                ),
            });
        }
        if (selectedProductOutputPortsInCartIds.length > 0) {
            submitFormIssues.push({
                key: 'selectedProductOutputPortsInCart',
                value: t(
                    'There are currently {{count}} Output Ports, that are part of your selected Data Product. Please remove them from the cart before proceeding.',
                    {
                        count: selectedProductOutputPortsInCartIds.length,
                    },
                ),
            });
        }

        return submitFormIssues;
    }, [overlappingOutputPortIds, selectedProductOutputPortsInCartIds]);
    const onFinish: FormProps<CartFormData>['onFinish'] = (values) => {
        if (
            !values.justification ||
            !values.dataProductId ||
            cartOutputPorts === undefined ||
            cartOutputPorts.length === 0
        ) {
            return;
        }
        posthog.capture(PosthogEvents.CART_CHECKOUT_COMPLETED_EXISTING_DATA_PRODUCT, {
            cartSize: cartOutputPorts?.length,
        });
        clearStorage();
        requestInputPortsForDataProduct({
            id: values.dataProductId,
            requestInputPortsForDataProductRequest: {
                output_ports: cartOutputPorts?.map((dataset) => dataset.id),
                justification: values.justification,
            },
        });
    };
    const currentUser = useSelector(selectCurrentUser);
    const { data: { data_products: userDataProducts = [] } = {}, isFetching: isFetchingUserDataProducts } =
        useGetDataProductsQuery(currentUser?.id, {
            skip: currentUser === null || !currentUser?.id,
        });
    const options = userDataProducts.map((dp) => ({
        value: dp.id,
        label: dp.name,
        description: dp.description,
    }));
    return (
        <Form<CartFormData> layout={'vertical'} form={form} onFinish={onFinish} onValuesChange={onValuesChange}>
            <Form.Item<CartFormData>
                name="dataProductId"
                label={t('Data Product')}
                rules={[{ required: true, message: t('Please select a Data Product') }]}
            >
                <Select
                    placeholder={t('Search Data Products')}
                    showSearch={{
                        optionFilterProp: 'label',
                    }}
                    autoFocus={isRestored && selectedDataProductId === undefined}
                    defaultOpen={isRestored && selectedDataProductId === undefined}
                    loading={isFetchingUserDataProducts}
                    options={options}
                    optionRender={(option) => (
                        <Space vertical>
                            <Typography.Text>{option.data.label}</Typography.Text>
                            <Typography.Text type="secondary">{option.data.description}</Typography.Text>
                        </Space>
                    )}
                />
            </Form.Item>
            <FormIssues submitFormIssues={submitFormIssues} />
            <JustificationFormItem />
            <FormItemAccessDuration
                cartOutputPorts={cartOutputPorts}
                dataProductTypeChoice={DataProductChoiceOptions.data_product}
            />
            <Form.Item label={null}>
                <Button
                    type="primary"
                    htmlType="submit"
                    style={{ width: '100%' }}
                    loading={isRequestingAccess}
                    disabled={
                        submitFormIssues.length > 0 || cartOutputPorts === undefined || cartOutputPorts?.length === 0
                    }
                >
                    {t('Submit access requests')}
                </Button>
            </Form.Item>
        </Form>
    );
};
