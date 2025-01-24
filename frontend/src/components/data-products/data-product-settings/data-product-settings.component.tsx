import styles from './data-product-settings.module.scss';
import { Flex, Form, FormProps, Select, Switch, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    useCreateDataProductSettingValueMutation,
    useGetAllDataProductSettingsQuery,
} from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { useEffect, useMemo, useRef } from 'react';
import { getIsDataProductOwner } from '@/utils/data-product-user-role.helper.ts';
import {
    DataProductSettingContract,
    DataProductSettingCreateRequest,
    DataProductSettingValueForm,
} from '@/types/data-product-setting';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import TextArea from 'antd/es/input/TextArea';

type Timeout = ReturnType<typeof setTimeout>; // Defines the type for timeouts
type Props = {
    dataProductId: string | undefined;
};

export function DataProductSettings({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isFetching: isFetchingDP } = useGetDataProductByIdQuery(dataProductId || '', {
        skip: !dataProductId,
    });
    const { data: settings, isFetching } = useGetAllDataProductSettingsQuery();
    const [updateSetting] = useCreateDataProductSettingValueMutation();
    const [form] = Form.useForm();
    const user = useSelector(selectCurrentUser);
    const timeoutRef = useRef<Timeout | null>(null);

    const isDataProductOwner = useMemo(() => {
        if (!dataProduct || !user) return false;

        return getIsDataProductOwner(dataProduct, user.id) || user.is_admin;
    }, [dataProduct?.id, user?.id]);

    const onSubmit: FormProps<DataProductSettingValueForm>['onFinish'] = async (values) => {
        try {
            if (dataProduct) {
                updatedSettings?.map(async (setting) => {
                    const key = `data_product_settings_id_${setting.id}`;
                    if (values[`value_${setting.id}`].toString() !== setting.value) {
                        const request: DataProductSettingCreateRequest = {
                            data_product_id: dataProduct.id,
                            data_product_settings_id: values[key],
                            value: values[`value_${setting.id}`].toString(),
                        };
                        await updateSetting(request).unwrap();
                        dispatchMessage({ content: t('Setting updated successfully'), type: 'success' });
                    }
                });
            }
        } catch (_e) {
            const errorMessage = 'Failed to update setting';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataProductSettingValueForm>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const updatedSettings: (DataProductSettingContract & { value: string })[] = useMemo(() => {
        if (settings) {
            return settings.map((setting) => {
                const match = dataProduct?.data_product_settings?.find(
                    (dps) => dps.data_product_setting_id === setting.id,
                );
                return match ? { ...setting, value: match.value } : { ...setting, value: setting.default };
            });
        } else {
            return [];
        }
    }, [settings, dataProduct]);
    useEffect(() => {
        updatedSettings.map((setting) => {
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
    }, [updatedSettings]);

    const settingsRender = useMemo(() => {
        // Group settings by divider
        const groupedSettings = updatedSettings.reduce(
            (groups, setting) => {
                const divider = setting.divider; // Use 'Default' for settings without a divider
                if (!groups[divider]) {
                    groups[divider] = [];
                }
                groups[divider].push(setting);
                return groups;
            },
            {} as Record<string, typeof updatedSettings>,
        );

        // Render grouped settings
        const formContent = Object.entries(groupedSettings).map(([divider, settings]) => (
            <Flex key={divider} vertical>
                <Typography.Title>{divider}</Typography.Title>
                {settings.map((setting) => {
                    let renderedSetting;
                    switch (setting.type) {
                        case 'checkbox':
                            renderedSetting = (
                                <Form.Item<DataProductSettingValueForm>
                                    name={`value_${setting.id}`}
                                    label={t(setting.name)}
                                    tooltip={t(setting.tooltip)}
                                    rules={[
                                        {
                                            required: true,
                                            message: t('Please input the value'),
                                        },
                                    ]}
                                >
                                    <Switch />
                                </Form.Item>
                            );
                            break;
                        case 'tags':
                            renderedSetting = (
                                <Form.Item<DataProductSettingValueForm>
                                    name={`value_${setting.id}`}
                                    label={t(setting.name)}
                                    tooltip={t(setting.tooltip)}
                                >
                                    <Select allowClear={false} defaultActiveFirstOption mode="tags" />
                                </Form.Item>
                            );
                            break;
                        case 'input':
                            renderedSetting = (
                                <Form.Item<DataProductSettingValueForm>
                                    name={`value_${setting.id}`}
                                    label={t(setting.name)}
                                    tooltip={t(setting.tooltip)}
                                >
                                    <TextArea rows={3} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
                                </Form.Item>
                            );
                            break;
                        default:
                            break;
                    }
                    return (
                        <Flex key={setting.id} vertical>
                            {/* Hidden Input for ID */}
                            <Form.Item<DataProductSettingValueForm>
                                name={`data_product_settings_id_${setting.id}`}
                                initialValue={setting.id}
                                hidden
                            />
                            {renderedSetting}
                        </Flex>
                    );
                })}
            </Flex>
        ));
        return (
            <Flex vertical>
                <Form
                    form={form}
                    labelCol={FORM_GRID_WRAPPER_COLS}
                    wrapperCol={FORM_GRID_WRAPPER_COLS}
                    layout="horizontal"
                    onFinish={onSubmit}
                    onFinishFailed={onSubmitFailed}
                    autoComplete={'off'}
                    requiredMark={'optional'}
                    labelWrap
                    labelAlign={'left'}
                    disabled={isFetching || isFetchingDP || !isDataProductOwner}
                    className={styles.form}
                    onValuesChange={(_, allValues) => {
                        if (timeoutRef.current) {
                            clearTimeout(timeoutRef.current);
                        }

                        // Set a new timeout to call onSubmit after 3 seconds
                        timeoutRef.current = setTimeout(() => {
                            onSubmit(allValues); // Trigger the onSubmit function
                        }, 1500);
                    }}
                >
                    {formContent}
                </Form>
            </Flex>
        );
    }, [updatedSettings, dataProduct]);
    return settingsRender;
}
