import { usePostHog } from '@posthog/react';
import { Button, Flex, Form, type FormProps } from 'antd';
import { useForm } from 'antd/es/form/Form';
import { t } from 'i18next';
import { useCallback, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import styles from '@/components/data-products/data-product-form/data-product-form.module.scss';
import { DataProductFormItems } from '@/components/data-products/data-product-form/data-product-form-items.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useFormPersist } from '@/hooks/use-form-persist.tsx';
import { JustificationFormItem } from '@/pages/cart/components/form-item-justification.tsx';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    type DataProductCreate,
    useCreateDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { clearCart } from '@/store/features/cart/cart-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { createDataProductIdPath } from '@/types/navigation.ts';

type NewDataProductCartFormData = DataProductCreate & {
    justification: string;
};
type Props = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
};

export const NewDataProductForm = ({ cartOutputPorts }: Props) => {
    const dispatch = useAppDispatch();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const [form] = useForm<NewDataProductCartFormData>();
    const [areFormItemsLoading, setAreFormItemsLoading] = useState(true);
    const currentUser = useSelector(selectCurrentUser);

    const [createDataProduct] = useCreateDataProductMutation();
    const [submitting, setSubmitting] = useState(false);
    const { onValuesChange, clearStorage } = useFormPersist<NewDataProductCartFormData>(
        form,
        'cart-new-data-product-form',
    );
    const onFinish: FormProps<NewDataProductCartFormData>['onFinish'] = useCallback(
        async (values) => {
            setSubmitting(true);
            try {
                const { justification, ...request } = values;
                if (cartOutputPorts === undefined || cartOutputPorts.length === 0) {
                    return;
                }
                const response = await createDataProduct({
                    ...request,
                    input_ports: {
                        justification,
                        output_ports: cartOutputPorts?.map((dataset) => dataset.id),
                    },
                }).unwrap();
                dispatch(clearCart());
                dispatchMessage({ content: t('Your requests have successfully been created.'), type: 'success' });
                posthog.capture(PosthogEvents.CART_CHECKOUT_COMPLETED_NEW_DATA_PRODUCT, {
                    cartSize: cartOutputPorts?.length,
                });
                clearStorage();
                navigate(createDataProductIdPath(response.id, DataProductTabKeys.InputPorts));
            } catch {
                dispatchMessage({ content: t('Failed to create Data Product. Please try again.'), type: 'error' });
            } finally {
                setSubmitting(false);
            }
        },
        [posthog, createDataProduct, navigate, clearStorage, cartOutputPorts, dispatch],
    );
    const initialValues = {
        owners: currentUser?.id ? [currentUser?.id] : [],
    };
    return (
        <Form<NewDataProductCartFormData>
            form={form}
            onFinish={onFinish}
            layout={'vertical'}
            autoComplete={'off'}
            onValuesChange={onValuesChange}
            initialValues={initialValues}
        >
            <DataProductFormItems form={form} mode={'create'} setAreFormItemsLoading={setAreFormItemsLoading} />
            <JustificationFormItem />
            <Form.Item>
                <Flex justify="end">
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={submitting}
                        disabled={areFormItemsLoading}
                    >
                        {t('Create')}
                    </Button>
                </Flex>
            </Form.Item>
        </Form>
    );
};
