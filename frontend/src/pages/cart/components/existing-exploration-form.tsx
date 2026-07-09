import { usePostHog } from '@posthog/react';
import { Button, Form, type FormProps, Select, Space, Typography } from 'antd';
import { t } from 'i18next';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { useFormPersist } from '@/hooks/use-form-persist.tsx';
import { AccessDurationOverview } from '@/pages/cart/components/access-duration-overview';
import { FormIssues } from '@/pages/cart/components/form-item-issues.tsx';
import { JustificationFormItem } from '@/pages/cart/components/form-item-justification.tsx';
import { useCartOverlapCheck } from '@/pages/cart/hooks/use-cart-overlap-check.ts';
import { ExplorationTabKeys } from '@/pages/exploration/exploration-tab-keys.ts';
import { useAppDispatch } from '@/store';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    useGetExplorationsQuery,
    useRequestInputPortsForExplorationMutation,
} from '@/store/api/services/generated/explorationsApi.ts';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { clearCart, DataProductChoiceOptions } from '@/store/features/cart/cart-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { createExplorationIdPath } from '@/types/navigation.ts';

type CartFormData = {
    explorationId?: string;
    justification?: string;
};

type Props = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
    setSelectedExplorationId: (id?: string) => void;
};

export const ExistingExplorationForm = ({ cartOutputPorts, setSelectedExplorationId }: Props) => {
    const dispatch = useAppDispatch();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);
    const { data: { explorations: userExplorations = [] } = {}, isFetching: isFetchingUserExplorations } =
        useGetExplorationsQuery(currentUser?.id, {
            skip: currentUser === null || !currentUser?.id,
        });

    const [requestInputPortsForExploration, { isSuccess: requestingAccessSuccess, isLoading: isRequestingAccess }] =
        useRequestInputPortsForExplorationMutation();
    const [form] = Form.useForm<CartFormData>();
    const selectedExplorationId = Form.useWatch('explorationId', form);
    const justification = Form.useWatch('justification', form);
    const [justificationPrefilled, setJustificationPrefilled] = useState(false);
    useEffect(() => {
        setSelectedExplorationId(selectedExplorationId);
        return () => {
            setSelectedExplorationId(undefined);
        };
    }, [selectedExplorationId, setSelectedExplorationId]);
    const handleUserTyping = useCallback(() => {
        if (justificationPrefilled) {
            setJustificationPrefilled(false);
        }
    }, [justificationPrefilled]);
    useEffect(() => {
        const selectedExploration = userExplorations.find((exp) => exp.id === selectedExplorationId);
        if (selectedExploration && !justification) {
            if (selectedExploration?.description && !justification) {
                form.setFieldsValue({ justification: selectedExploration.description });
                setJustificationPrefilled(true);
            }
        }
    }, [selectedExplorationId, userExplorations, form, justification]);
    const { onValuesChange, clearStorage, isRestored } = useFormPersist<CartFormData>(
        form,
        'cart-existing-exploration-form',
    );

    const { overlappingOutputPortIds } = useCartOverlapCheck({
        selectedExplorationId,
    });

    useEffect(() => {
        if (requestingAccessSuccess && selectedExplorationId) {
            dispatch(clearCart());
            dispatchMessage({ content: t('Your requests have successfully been created.'), type: 'success' });

            navigate(createExplorationIdPath(selectedExplorationId, ExplorationTabKeys.InputPorts));
        }
    }, [requestingAccessSuccess, selectedExplorationId, dispatch, navigate]);
    const submitFormIssues = useMemo(() => {
        const submitFormIssues = [];
        if (overlappingOutputPortIds.length > 0) {
            submitFormIssues.push({
                key: 'overlappingOutputPortId',
                value: t(
                    'There are currently {{count}} Output Ports in the cart, for which the selected Exploration already has access, or has an access request. Please remove them from the cart before proceeding.',
                    {
                        count: overlappingOutputPortIds.length,
                    },
                ),
            });
        }
        return submitFormIssues;
    }, [overlappingOutputPortIds]);
    const onFinish: FormProps<CartFormData>['onFinish'] = (values) => {
        if (
            !values.justification ||
            !values.explorationId ||
            cartOutputPorts === undefined ||
            cartOutputPorts.length === 0
        ) {
            return;
        }
        posthog.capture(PosthogEvents.CART_CHECKOUT_COMPLETED_EXISTING_EXPLORATION, {
            cartSize: cartOutputPorts?.length,
        });
        clearStorage();
        requestInputPortsForExploration({
            id: values.explorationId,
            requestInputPortsForExplorationRequest: {
                output_ports: cartOutputPorts?.map((dataset) => dataset.id),
                justification: values.justification,
            },
        });
    };
    return (
        <Form<CartFormData> layout={'vertical'} form={form} onFinish={onFinish} onValuesChange={onValuesChange}>
            <Form.Item<CartFormData>
                name="explorationId"
                label={t('Exploration')}
                rules={[{ required: true, message: t('Please select an Exploration') }]}
            >
                <Select
                    placeholder={t('Search Exploration')}
                    showSearch={{
                        optionFilterProp: 'label',
                    }}
                    autoFocus={isRestored && selectedExplorationId === undefined}
                    defaultOpen={isRestored && selectedExplorationId === undefined}
                    loading={isFetchingUserExplorations}
                    options={userExplorations.map((exp) => ({
                        value: exp.id,
                        label: exp.name,
                        description: exp.description,
                    }))}
                    optionRender={(option) => (
                        <Space vertical>
                            <Typography.Text>{option.data.label}</Typography.Text>
                            <Typography.Text type="secondary">{option.data.description}</Typography.Text>
                        </Space>
                    )}
                />
            </Form.Item>
            <FormIssues submitFormIssues={submitFormIssues} />
            <JustificationFormItem
                extra={
                    justificationPrefilled ? (
                        <Typography.Text type="warning">
                            {t('Pre-filled from the Exploration description. Please review before submitting.')}
                        </Typography.Text>
                    ) : undefined
                }
                onChange={handleUserTyping}
            />
            <AccessDurationOverview
                cartOutputPorts={cartOutputPorts}
                dataProductTypeChoice={DataProductChoiceOptions.exploration}
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
