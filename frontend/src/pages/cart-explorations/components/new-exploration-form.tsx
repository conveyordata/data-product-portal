import { usePostHog } from '@posthog/react';
import { Button, Flex, Form, type FormProps, Input, Select } from 'antd';
import { useForm } from 'antd/es/form/Form';
import TextArea from 'antd/es/input/TextArea';
import { t } from 'i18next';
import { useCallback, useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useDebouncedCallback } from 'use-debounce';
import styles from '@/components/data-products/data-product-form/data-product-form.module.scss';
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useFormPersist } from '@/hooks/use-form-persist.tsx';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import type { DataProductCreate } from '@/store/api/services/generated/dataProductsApi.ts';
import { useCreateExplorationMutation } from '@/store/api/services/generated/explorationsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import {
    ResourceNameModel,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
    useResourceNameConstraintsQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { clearCart } from '@/store/features/cart/cart-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';

type Props = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
};

type CreateExplorationRequestForm = {
    name: string;
    namespace: string;
    description: string;
    domain_id: string;
    justification: string;
};

export const NewExplorationForm = ({ cartOutputPorts }: Props) => {
    const dispatch = useAppDispatch();
    const posthog = usePostHog();
    const [form] = useForm<CreateExplorationRequestForm>();
    const { data: { domains = [] } = {}, isFetching: isFetchingDomains } = useGetDomainsQuery();
    const currentUser = useSelector(selectCurrentUser);

    const [createExploration, { isLoading: isCreatingExploration }] = useCreateExplorationMutation();
    const { onValuesChange, clearStorage } = useFormPersist<CreateExplorationRequestForm>(
        form,
        'cart-new-exploration-form',
    );
    const dataProductNameValue = Form.useWatch('name', form);
    const [canEditResourceName, setCanEditResourceName] = useState<boolean>(false);
    const [sanitizeResourceName, { data: sanitizedResourceName, isSuccess: sanitizedResourceNameSuccess }] =
        useLazySanitizeResourceNameQuery();
    const fetchResourceNameDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), 500);
    useEffect(() => {
        if (!canEditResourceName) {
            form.setFields([
                {
                    name: 'namespace',
                    validating: true,
                    errors: [],
                },
            ]);
            fetchResourceNameDebounced(dataProductNameValue ?? '');
        }
    }, [form, canEditResourceName, dataProductNameValue, fetchResourceNameDebounced]);

    useEffect(() => {
        if (!canEditResourceName && sanitizedResourceNameSuccess && sanitizedResourceName) {
            form.setFieldValue('namespace', sanitizedResourceName.resource_name);
            form.validateFields(['namespace']);
        }
    }, [form, canEditResourceName, sanitizedResourceName, sanitizedResourceNameSuccess]);

    const onFinish: FormProps<CreateExplorationRequestForm>['onFinish'] = useCallback(
        async (values: CreateExplorationRequestForm) => {
            try {
                if (cartOutputPorts === undefined || cartOutputPorts.length === 0) {
                    console.error('No items in cart');
                    return;
                }
                const { justification, ...request } = values;
                await createExploration({
                    input_ports: {
                        output_ports: cartOutputPorts?.map((dataset) => dataset.id),
                        justification,
                    },
                    ...request,
                }).unwrap();
                dispatch(clearCart());
                dispatchMessage({ content: t('Your Exploration has been created.'), type: 'success' });
                posthog.capture(PosthogEvents.CART_CHECKOUT_COMPLETED_NEW_DATA_PRODUCT, {
                    cartSize: cartOutputPorts?.length,
                });
                clearStorage();
                //Enable once we have the first draft of exploration
                //navigate(createExplorationIdPath(response.id, DataProductTabKeys.InputPorts));
            } catch {
                dispatchMessage({ content: t('Failed to create Exploration. Please try again.'), type: 'error' });
            }
        },
        [posthog, createExploration, clearStorage, cartOutputPorts, dispatch],
    );
    const initialValues = {
        owners: currentUser?.id ? [currentUser?.id] : [],
    };
    const [validateResourceName, { isFetching: validatingResourceName }] = useLazyValidateResourceNameQuery();
    const { data: constraints, isFetching: loadingResourceNameConstraints } = useResourceNameConstraintsQuery();
    const resourceNameValidationCallback = useCallback(
        (resourceName: string) =>
            validateResourceName({
                resourceName: resourceName,
                model: ResourceNameModel.Exploration,
            }).unwrap(),
        [validateResourceName],
    );
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
            <ResourceNameFormItem
                form={form}
                tooltip={t('The namespace of the Data Product')}
                max_length={constraints?.max_length}
                editToggleDisabled={false}
                canEditResourceName={canEditResourceName}
                toggleCanEditResourceName={() => setCanEditResourceName((prev) => !prev)}
                validationRequired
                validateResourceName={resourceNameValidationCallback}
            />
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
            <Form.Item<CreateExplorationRequestForm>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Data Product'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than {{length}} characters', {
                            length: MAX_DESCRIPTION_INPUT_LENGTH,
                        }),
                    },
                ]}
            >
                <TextArea rows={4} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item<CreateExplorationRequestForm>
                name="justification"
                label={t('Business justification')}
                rules={[
                    {
                        required: true,
                        message: t('Please explain why you need access to these Output Ports'),
                    },
                ]}
            >
                <TextArea rows={4} placeholder={t('Explain why you need access to these Output Ports')} />
            </Form.Item>
            <Form.Item>
                <Flex justify="end">
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreatingExploration}
                        disabled={isFetchingDomains || validatingResourceName || loadingResourceNameConstraints}
                    >
                        {t('Create')}
                    </Button>
                </Flex>
            </Form.Item>
        </Form>
    );
};
