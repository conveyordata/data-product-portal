import { usePostHog } from '@posthog/react';
import { Button, Flex, Form, type FormProps, Input, Select } from 'antd';
import { useForm } from 'antd/es/form/Form';
import { t } from 'i18next';
import { useCallback, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import { useDebouncedCallback } from 'use-debounce';
import styles from '@/components/data-products/data-product-form/data-product-form.module.scss';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useFormPersist } from '@/hooks/use-form-persist.tsx';
import { FormItemAccessDuration } from '@/pages/cart/components/form-item-access-duration.tsx';
import { JustificationFormItem } from '@/pages/cart/components/form-item-justification.tsx';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import type { DataProductCreate } from '@/store/api/services/generated/dataProductsApi.ts';
import { useCreateExplorationMutation } from '@/store/api/services/generated/explorationsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import {
    ResourceNameModel,
    ResourceNameValidityType,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { clearCart, DataProductChoiceOptions } from '@/store/features/cart/cart-slice.ts';
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
    const dataProductNameValue = Form.useWatch('name', form);
    const [
        sanitizeResourceName,
        { data: sanitizedResourceName, isSuccess: sanitizedResourceNameSuccess, isFetching: sanitizingResourceName },
    ] = useLazySanitizeResourceNameQuery();
    const fetchResourceNameDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), 500);
    const isResourceNamePending = fetchResourceNameDebounced.isPending();
    useEffect(() => {
        fetchResourceNameDebounced(dataProductNameValue ?? '');
    }, [dataProductNameValue, fetchResourceNameDebounced]);

    const onFinish: FormProps<CreateExplorationRequestForm>['onFinish'] = useCallback(
        async (values: CreateExplorationRequestForm) => {
            try {
                if (cartOutputPorts === undefined || cartOutputPorts.length === 0) {
                    console.error('No items in cart');
                    return;
                }
                if (!sanitizedResourceNameSuccess || sanitizedResourceName === undefined) {
                    console.error('resource name should be fetched first');
                    return;
                }
                const { justification, ...request } = values;
                const response = await createExploration({
                    //For an Exploration we use the justification as description
                    //since the meaning should be the same for an exploration
                    description: justification,
                    namespace: sanitizedResourceName.resource_name,
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
                navigate(createExplorationIdPath(response.id));
            } catch {
                dispatchMessage({ content: t('Failed to create Exploration. Please try again.'), type: 'error' });
            }
        },
        [
            posthog,
            createExploration,
            clearStorage,
            cartOutputPorts,
            dispatch,
            navigate,
            sanitizedResourceNameSuccess,
            sanitizedResourceName,
        ],
    );
    const initialValues = {
        owners: currentUser?.id ? [currentUser?.id] : [],
    };
    const [validateResourceName, { data: validationResult, isFetching: validatingResourceName }] =
        useLazyValidateResourceNameQuery();
    useEffect(() => {
        if (sanitizedResourceName?.resource_name) {
            validateResourceName({
                resourceName: sanitizedResourceName?.resource_name,
                model: ResourceNameModel.Exploration,
            });
        }
    }, [sanitizedResourceName, validateResourceName]);
    useEffect(() => {
        if (validationResult && validationResult.validity !== ResourceNameValidityType.Valid) {
            const errorMessages: Record<string, string> = {
                [ResourceNameValidityType.Duplicate]: t('An Exploration with this name already exists'),
                [ResourceNameValidityType.InvalidLength]: t('The name of the Exploration is too long'),
            };
            form.setFields([
                {
                    name: 'name',
                    errors: [errorMessages[validationResult.validity] ?? t('Invalid Exploration name')],
                },
            ]);
        } else if (validationResult?.validity === ResourceNameValidityType.Valid) {
            form.setFields([
                {
                    name: 'name',
                    errors: [],
                },
            ]);
        }
    }, [validationResult, form]);
    return (
        <Form<CreateExplorationRequestForm>
            form={form}
            onFinish={onFinish}
            layout={'vertical'}
            onValuesChange={onValuesChange}
            autoComplete={'off'}
            initialValues={initialValues}
        >
            <Form.Item<DataProductCreate>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Exploration')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Exploration'),
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
                        message: t('Please select the domain of the Exploration'),
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
            <FormItemAccessDuration
                cartOutputPorts={cartOutputPorts}
                dataProductTypeChoice={DataProductChoiceOptions.exploration}
            />
            <Form.Item>
                <Flex justify="end">
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreatingExploration}
                        disabled={
                            isFetchingDomains ||
                            sanitizingResourceName ||
                            validatingResourceName ||
                            isResourceNamePending
                        }
                    >
                        {t('Create')}
                    </Button>
                </Flex>
            </Form.Item>
        </Form>
    );
};
