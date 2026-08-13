import { Form, Input, Modal, Select } from 'antd';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
    useCreateAccessModeMutation,
    useUpdateAccessModeMutation,
} from '@/store/api/services/generated/configurationAccessModesApi.ts';
import type { AccessMode } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi.ts';
import { isCanNotRemoveTechnicalAssetTypesError } from '@/store/common/api-errors.ts';
import { showGenericErrorMessage } from '@/store/common/errors.ts';

const { TextArea } = Input;

type Props = {
    onClose: () => void;
    editAccessMode?: AccessMode;
};
type AccessModeValues = {
    name: string;
    description: string;
    technical_asset_types: string[];
};
export default function AccessModesModal({ editAccessMode, onClose }: Props) {
    const { t } = useTranslation();
    const mode = editAccessMode === undefined ? 'create' : 'edit';
    const [form] = Form.useForm<AccessModeValues>();
    const { data: { plugins = [] } = {}, isFetching: isFetchingPlugins } = useGetPluginsQuery();

    const [createAccessMode] = useCreateAccessModeMutation();
    const [updateAccessMode] = useUpdateAccessModeMutation();
    const onFinish = useCallback(
        async (values: AccessModeValues) => {
            switch (mode) {
                case 'create':
                    await createAccessMode(values).unwrap();
                    onClose();
                    return;
                case 'edit': {
                    try {
                        await updateAccessMode({
                            id: editAccessMode?.id ?? '',
                            accessModeUpdate: {
                                description: values.description,
                                technical_asset_types: values.technical_asset_types,
                            },
                        }).unwrap();
                    } catch (error) {
                        if (isCanNotRemoveTechnicalAssetTypesError(error)) {
                            form.setFields([
                                {
                                    name: 'technical_asset_types',
                                    errors: [
                                        t(
                                            'You cannot remove Technical Asset types that are still used by Technical Assets',
                                        ),
                                    ],
                                },
                            ]);
                            return;
                        }
                        showGenericErrorMessage(error);
                    }
                    onClose();
                    return;
                }
            }
        },
        [mode, createAccessMode, updateAccessMode, editAccessMode, form, onClose, t],
    );

    return (
        <Modal
            centered
            title={mode === 'create' ? t('Create Access Mode') : t('Edit Access Mode')}
            open={true}
            onOk={() => form.submit()}
            onCancel={onClose}
        >
            <Form<AccessModeValues> form={form} layout="vertical" initialValues={editAccessMode} onFinish={onFinish}>
                <Form.Item<AccessModeValues>
                    name="name"
                    label={t('Name')}
                    required={mode === 'create'}
                    rules={[{ required: true, message: t('Please provide the name of the access mode') }]}
                >
                    <Input placeholder="Name" disabled={mode === 'edit'} />
                </Form.Item>
                <Form.Item<AccessModeValues>
                    name="technical_asset_types"
                    label={t('Technical Asset types')}
                    required={mode === 'create'}
                    rules={[
                        {
                            required: true,
                            message: t('Please provide at least one Technical Asset type for the access mode'),
                        },
                    ]}
                >
                    <Select
                        loading={isFetchingPlugins}
                        onChange={() => form.setFields([{ name: 'technical_asset_types', errors: [] }])}
                        options={plugins
                            .filter((plugin) => plugin.show_in_form)
                            .map((plugin) => ({
                                label: t(plugin.display_name),
                                value: plugin.plugin,
                            }))}
                        mode="multiple"
                    />
                </Form.Item>
                <Form.Item<AccessModeValues>
                    name="description"
                    label={t('Description')}
                    required
                    rules={[{ required: true, message: t('Please provide the description of the access mode') }]}
                >
                    <TextArea rows={4} />
                </Form.Item>
            </Form>
        </Modal>
    );
}
