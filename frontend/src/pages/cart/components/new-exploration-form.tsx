import { usePostHog } from '@posthog/react';
import { Button, Flex, Form, type FormProps, Input, Select } from 'antd';
import { useForm } from 'antd/es/form/Form';
import { t } from 'i18next';
import { useCallback } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import styles from '@/components/data-products/data-product-form/data-product-form.module.scss';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useFormPersist } from '@/hooks/use-form-persist.tsx';
import { JustificationFormItem } from '@/pages/cart/components/form-item-justification.tsx';
import { ExplorationTabKeys } from '@/pages/exploration/exploration-tab-keys.ts';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import type { DataProductCreate } from '@/store/api/services/generated/dataProductsApi.ts';
import { useCreateExplorationMutation } from '@/store/api/services/generated/explorationsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { clearCart } from '@/store/features/cart/cart-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { createExplorationIdPath } from '@/types/navigation.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';

type Props = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
};

type CreateExplorationRequestForm = {
    name: string;
    domain_id: string;
    justification: string;
};

export const NewExplorationForm = ({ cartOutputPorts }: Props) => {
    const dispatch = useAppDispatch();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const [form] = useForm<CreateExplorationRequestForm>();
    const { data: { domains = [] } = {}, isFetching: isFetchingDomains } = useGetDomainsQuery();
    const currentUser = useSelector(selectCurrentUser);

    const [createExploration, { isLoading: isCreatingExploration }] = useCreateExplorationMutation();
    const { onValuesChange, clearStorage } = useFormPersist<CreateExplorationRequestForm>(
        form,
        'cart-new-exploration-form',
    );

    const onFinish: FormProps<CreateExplorationRequestForm>['onFinish'] = useCallback(
        async (values: CreateExplorationRequestForm) => {
            try {
                if (cartOutputPorts === undefined || cartOutputPorts.length === 0) {
                    console.error('No items in cart');
                    return;
                }
                const { justification, ...request } = values;
                const response = await createExploration({
                    description: justification,
                    input_ports: {
                        output_ports: cartOutputPorts?.map((dataset) => dataset.id),
                        justification,
                    },
                    ...request,
                }).unwrap();
                dispatch(clearCart());
                dispatchMessage({ content: t('Your Exploration has been created.'), type: 'success' });
                posthog.capture(PosthogEvents.CART_CHECKOUT_COMPLETED_NEW_EXPLORATION, {
                    cartSize: cartOutputPorts?.length,
                });
                clearStorage();
                navigate(createExplorationIdPath(response.id, ExplorationTabKeys.InputPorts));
            } catch {
                dispatchMessage({ content: t('Failed to create Exploration. Please try again.'), type: 'error' });
            }
        },
        [posthog, createExploration, clearStorage, cartOutputPorts, dispatch, navigate],
    );
    const initialValues = {
        owners: currentUser?.id ? [currentUser?.id] : [],
    };
    return (
        <Form<CreateExplorationRequestForm>
            form={form}
            onFinish={onFinish}
            layout={'vertical'}
            onValuesChange={onValuesChange}
            initialValues={initialValues}
        >
            <Form.Item<DataProductCreate>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Data Product'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<CreateExplorationRequestForm>
                name={'domain_id'}
                label={t('Domain')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the domain of the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDomains}
                    options={domains.map((domain) => ({ label: domain.name, value: domain.id }))}
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    allowClear
                />
            </Form.Item>
            <JustificationFormItem />
            <Form.Item>
                <Flex justify="end">
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreatingExploration}
                        disabled={isFetchingDomains}
                    >
                        {t('Create')}
                    </Button>
                </Flex>
            </Form.Item>
        </Form>
    );
};
