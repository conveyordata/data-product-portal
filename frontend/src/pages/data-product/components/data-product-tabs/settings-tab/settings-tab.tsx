import styles from './settings-tab.module.scss';
import { Button, Flex, Form, FormProps, Input, Switch, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCreateDataProductSettingMutation, useGetAllDataProductSettingsQuery } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { useMemo } from 'react';
import {DataProductSettingContract, DataProductSettingCreateRequest} from '@/types/data-product-setting';
import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';

type Props = {
    dataProductId: string;
};

export function SettingsTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isFetching: isFetchingDP } = useGetDataProductByIdQuery(dataProductId);
    const {data: settings, isFetching} = useGetAllDataProductSettingsQuery()
    const [updateSetting] = useCreateDataProductSettingMutation();
    const [form] = Form.useForm();

    const onSubmit: FormProps<DataProductSettingCreateRequest>['onFinish'] = async (values) => {
        try {
            if (dataProduct) {
                updatedSettings?.map(async (setting) => {
                    const key = `data_product_settings_id_${setting.id}`;
                    if (values[setting.id].toString() !== setting.value) {
                        const request: DataProductSettingCreateRequest = {
                            data_product_id: dataProduct.id,
                            data_product_settings_id: values[key],
                            value: values[setting.id].toString()
                        };
                        await updateSetting(request).unwrap();
                        dispatchMessage({ content: t('Setting updated successfully'), type: 'success' });
                    }
                    // modalCallbackOnSubmit();
                    // navigate(createDataProductIdPath(dataProductId, TabKeys.DataOutputs));
                    // form.resetFields();
                })

            }
        } catch (_e) {
            const errorMessage = 'Failed to update setting';
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataProductSettingCreateRequest>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const updatedSettings: (DataProductSettingContract&{value: string})[] = useMemo(() => {
    if (settings && dataProduct) {
        return settings.map(setting => {
            const match = dataProduct?.data_product_settings?.find(dps => dps.data_product_setting_id === setting.id);
            return match ? { ...setting, value: match.value } : {...setting, value: setting.default};
          });
    } else {
        return [];
    }
}, [settings, dataProduct])


    const settingsRender = useMemo(() => {

        // TODO Somehow do a grouping per divider

        const formContent = updatedSettings.map(setting => {
            let renderedSetting;
            switch (setting.type) {
                case "checkbox":
                    renderedSetting =
                    <Flex key={setting.id} vertical>
                    {setting.divider && (
                        <Typography.Title>{setting.divider}</Typography.Title>
                    )}
                    {/* Hidden Input for ID */}
                    <Form.Item<DataProductSettingCreateRequest>
                        name={`data_product_settings_id_${setting.id}`}
                        initialValue={setting.id}
                        hidden
                    >
                        <></>
                    </Form.Item>
                    <Form.Item<DataProductSettingCreateRequest>
                        //name={'value'}
                        name={setting.id}
                        label={t(setting.name)}
                        tooltip={t(setting.tooltip)}
                        rules={[
                            {
                                required: true,
                                message: t('Please input the value'),
                            },
                        ]}
                        initialValue={setting.value === "true"}
                    >
                        <Switch defaultValue={setting.value === "true"}/>
                    </Form.Item>
                    </Flex>
                    break;
                default:
                    break;
            }
            return renderedSetting
        })
        return <Flex vertical>
                <Form
                    form={form}
                    //labelCol={FORM_GRID_WRAPPER_COLS}
                    wrapperCol={FORM_GRID_WRAPPER_COLS}
                    layout="horizontal"
                    onFinish={onSubmit}
                    onFinishFailed={onSubmitFailed}
                    autoComplete={'off'}
                    requiredMark={'optional'}
                    labelWrap
                    labelAlign={'left'}
                    disabled={isFetching || isFetchingDP}
                    className={styles.form}
                >
                {formContent}
                <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isFetching || isFetchingDP}
                        disabled={isFetching || isFetchingDP}
                    >
                        {t('Update settings')}
                    </Button>
                </Form>

                </Flex>
    }, [settings, dataProduct])

    return (
        <>
            <Flex vertical className={styles.container}>
                {settingsRender}
            </Flex>
        </>
    );
}
