import { QuestionCircleOutlined } from '@ant-design/icons';
import {
    Descriptions,
    type DescriptionsProps,
    Empty,
    Flex,
    Form,
    type FormProps,
    Input,
    Select,
    Switch,
    Tooltip,
    Typography,
    theme,
} from 'antd';
import { type ReactElement, useCallback, useEffect, useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { DESCRIPTIONS_LABEL_WIDTH, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type DataProductSettingsGetItem,
    useGetDataProductsSettingsQuery,
} from '@/store/api/services/generated/configurationDataProductSettingsApi.ts';
import {
    type SetValueForDataProductApiArg,
    useGetDataProductSettingsQuery,
    useSetValueForDataProductMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import {
    type SetValueForOutputPortApiArg,
    useGetOutputPortQuery,
    useSetValueForOutputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { dispatchMessage } from '@/utils/feedback.ts';

const { TextArea } = Input;

type Timeout = ReturnType<typeof setTimeout>; // Defines the type for timeouts
type Props = {
    id: string;
    dataProductId?: string;
    scope: 'dataproduct' | 'dataset';
};

interface DataProductSettingValueForm {
    [id: string]: string;
}

export function DataProductSettings({ id, scope, dataProductId }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const { data: { data_product_settings: dataProductSettings = [] } = {}, isFetching: isFetchingDP } =
        useGetDataProductSettingsQuery(id || '', {
            skip: scope !== 'dataproduct',
        });
    const { data: outputPort, isFetching: isFetchingDS } = useGetOutputPortQuery(
        { id: id, dataProductId: dataProductId ?? '' },
        {
            skip: scope !== 'dataset' || !dataProductId,
        },
    );
    const { data: settings, isFetching } = useGetDataProductsSettingsQuery();
    const filteredSettings = useMemo(() => {
        return settings?.data_product_settings.filter((setting) => setting.scope === scope);
    }, [scope, settings]);

    const { data: product_access } = useCheckAccessQuery(
        {
            resource: id,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS,
        },
        { skip: scope !== 'dataproduct' },
    );
    const { data: output_port_access } = useCheckAccessQuery(
        {
            resource: id,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_SETTINGS,
        },
        { skip: scope !== 'dataset' },
    );

    const canUpdateProductSettings = product_access?.allowed || scope === 'dataset';
    const canUpdateOutputPortSetting = output_port_access?.allowed || scope === 'dataproduct';

    const [updateDataProductSetting] = useSetValueForDataProductMutation();
    const [updateOutputPortSetting] = useSetValueForOutputPortMutation();

    const [form] = Form.useForm();
    const timeoutRef = useRef<Timeout | null>(null);

    const updatedSettings: (DataProductSettingsGetItem & { value: string })[] = useMemo(() => {
        if (filteredSettings) {
            if (scope === 'dataproduct') {
                return filteredSettings.map((setting) => {
                    const match = dataProductSettings.find((dps) => dps.data_product_setting_id === setting.id);
                    return match ? { ...setting, value: match.value } : { ...setting, value: setting.default };
                });
            }
            if (scope === 'dataset') {
                return filteredSettings.map((setting) => {
                    const match = outputPort?.data_product_settings?.find(
                        (ds) => ds.data_product_setting_id === setting.id,
                    );
                    return match ? { ...setting, value: match.value } : { ...setting, value: setting.default };
                });
            }
        }
        return [];
    }, [filteredSettings, scope, dataProductSettings, outputPort?.data_product_settings]);

    const onSubmit: FormProps<DataProductSettingValueForm>['onFinish'] = useCallback(
        async (values: DataProductSettingValueForm) => {
            try {
                await Promise.all(
                    updatedSettings?.map(async (setting) => {
                        const key = `data_product_settings_id_${setting.id}`;
                        if (values[`value_${setting.id}`].toString() !== setting.value) {
                            if (scope === 'dataset') {
                                const request: SetValueForOutputPortApiArg = {
                                    id: id,
                                    dataProductId: dataProductId ?? '',
                                    settingId: values[key],
                                    value: values[`value_${setting.id}`].toString(),
                                };
                                return updateOutputPortSetting(request).unwrap();
                            }
                            if (scope === 'dataproduct') {
                                const request: SetValueForDataProductApiArg = {
                                    id: id,
                                    settingId: values[key],
                                    value: values[`value_${setting.id}`].toString(),
                                };
                                return updateDataProductSetting(request).unwrap();
                            }
                        }
                    }) ?? [],
                );
                dispatchMessage({ content: t('Setting updated successfully'), type: 'success' });
            } catch (_e) {
                const errorMessage = 'Failed to update setting';
                dispatchMessage({ content: errorMessage, type: 'error' });
            }
        },
        [updateOutputPortSetting, updatedSettings, updateDataProductSetting, t, scope, id, dataProductId],
    );

    const onSubmitFailed: FormProps<DataProductSettingValueForm>['onFinishFailed'] = useCallback(() => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    }, [t]);

    useEffect(() => {
        updatedSettings.forEach((setting) => {
            switch (setting.type) {
                case 'checkbox':
                    form.setFieldsValue({ [`value_${setting.id}`]: setting.value === 'true' });
                    break;
                case 'tags':
                    form.setFieldsValue({
                        [`value_${setting.id}`]: setting.value !== '' ? setting.value.split(',') : [],
                    });
                    break;
                case 'input':
                    form.setFieldsValue({ [`value_${setting.id}`]: setting.value });
                    break;
                default:
                    break;
            }
        });
    }, [form, updatedSettings]);

    const formContent = useMemo(() => {
        const renderControl = (setting: DataProductSettingsGetItem): ReactElement | null => {
            switch (setting.type) {
                case 'checkbox':
                    return (
                        <Form.Item<DataProductSettingValueForm>
                            name={`value_${setting.id}`}
                            style={{ margin: 0 }}
                            rules={[
                                {
                                    required: true,
                                    message: t('Please provide the value'),
                                },
                            ]}
                        >
                            <Switch />
                        </Form.Item>
                    );
                case 'tags':
                    return (
                        <Form.Item<DataProductSettingValueForm> name={`value_${setting.id}`} style={{ margin: 0 }}>
                            <Select allowClear={false} defaultActiveFirstOption mode="tags" />
                        </Form.Item>
                    );
                case 'input':
                    return (
                        <Form.Item<DataProductSettingValueForm> name={`value_${setting.id}`}>
                            <TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
                        </Form.Item>
                    );
                default:
                    return null;
            }
        };

        const items: DescriptionsProps['items'] = updatedSettings.map((setting) => ({
            key: setting.id,
            label: (
                <Flex vertical gap={0}>
                    <Flex align="center" gap="small">
                        <span>{setting.name}</span>
                        {setting.tooltip ? (
                            <Tooltip title={setting.tooltip}>
                                <QuestionCircleOutlined style={{ color: token.colorTextTertiary }} />
                            </Tooltip>
                        ) : null}
                    </Flex>
                    <Typography.Text type="secondary" style={{ fontSize: token.fontSizeSM }}>
                        {t('Category')}: {setting.category}
                    </Typography.Text>
                </Flex>
            ),
            children: (
                <>
                    <Form.Item<DataProductSettingValueForm>
                        name={`data_product_settings_id_${setting.id}`}
                        initialValue={setting.id}
                        hidden
                    />
                    {renderControl(setting)}
                </>
            ),
        }));

        return (
            <Descriptions
                column={1}
                size="small"
                bordered
                items={items}
                styles={{ label: { color: token.colorTextSecondary, width: DESCRIPTIONS_LABEL_WIDTH } }}
            />
        );
    }, [updatedSettings, t, token]);
    const isLoading = isFetching || isFetchingDP || isFetchingDS;
    if (!isLoading && updatedSettings.length === 0) return <Empty description="No settings to show" />;

    return (
        <Form
            form={form}
            onFinish={onSubmit}
            onFinishFailed={onSubmitFailed}
            autoComplete="off"
            disabled={isLoading || !canUpdateProductSettings || !canUpdateOutputPortSetting}
            onValuesChange={(_, allValues) => {
                // Trigger form submission after 0.5 seconds of unchanged input values
                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }

                timeoutRef.current = setTimeout(() => {
                    onSubmit(allValues); // Trigger the onSubmit function
                }, 500);
            }}
        >
            {formContent}
        </Form>
    );
}
