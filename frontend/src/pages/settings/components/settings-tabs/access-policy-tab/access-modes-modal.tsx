import { Form, Input, Modal } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type TechnicalAssetTypeSelection,
    TechnicalAssetTypesTable,
} from '@/pages/settings/components/settings-tabs/access-policy-tab/technical-asset-types-table.tsx';
import {
    type AccessModeWithType,
    useCreateAccessModeMutation,
    useGetAccessModesQuery,
    useUpdateAccessModeMutation,
} from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi.ts';

const { TextArea } = Input;

type Props = {
    onClose: () => void;
    editAccessMode?: AccessModeWithType;
};
type AccessModeValues = {
    name: string;
    description: string;
    technical_asset_types: TechnicalAssetTypeSelection;
};
export default function AccessModesModal({ editAccessMode, onClose }: Props) {
    const { t } = useTranslation();
    const mode = editAccessMode === undefined ? 'create' : 'edit';
    const [form] = Form.useForm<AccessModeValues>();
    const { data: { plugins = [] } = {}, isFetching: isFetchingPlugins } = useGetPluginsQuery();
    const { data: { access_modes: accessModes = [] } = {}, isFetching: isFetchingAccessModes } =
        useGetAccessModesQuery();

    const technicalAssetTypeOptions = useMemo(
        () =>
            plugins
                .filter((plugin) => plugin.show_in_form)
                .map((plugin) => ({ label: t(plugin.display_name), value: plugin.plugin })),
        [plugins, t],
    );
    const otherAccessModes = useMemo(
        () => accessModes.filter((accessMode) => accessMode.id !== editAccessMode?.id),
        [accessModes, editAccessMode],
    );
    const typesWithOtherDefault = useMemo(
        () => new Set(otherAccessModes.flatMap((accessMode) => accessMode.default_for_technical_asset_types)),
        [otherAccessModes],
    );
    const lockedTypes = useMemo(() => {
        const typesWithOtherAccessModes = new Set(
            otherAccessModes.flatMap((accessMode) => accessMode.technical_asset_types),
        );
        const locked = new Map<string, string>();
        for (const type of editAccessMode?.default_for_technical_asset_types ?? []) {
            if (typesWithOtherAccessModes.has(type)) {
                locked.set(type, t('Make another access mode the default for this type before removing it'));
            }
        }
        for (const type of editAccessMode?.in_use_technical_asset_types ?? []) {
            locked.set(type, t('Technical Assets of this type still use this access mode'));
        }
        return locked;
    }, [otherAccessModes, editAccessMode, t]);

    const [createAccessMode] = useCreateAccessModeMutation();
    const [updateAccessMode] = useUpdateAccessModeMutation();
    const onFinish = useCallback(
        async ({ name, description, technical_asset_types }: AccessModeValues) => {
            try {
                if (editAccessMode) {
                    await updateAccessMode({
                        id: editAccessMode.id,
                        accessModeUpdate: { description, ...technical_asset_types },
                    }).unwrap();
                } else {
                    await createAccessMode({ name, description, ...technical_asset_types }).unwrap();
                }
                onClose();
            } catch {
                // The request already showed its error, so the modal stays open.
            }
        },
        [createAccessMode, updateAccessMode, editAccessMode, onClose],
    );

    return (
        <Modal
            centered
            title={mode === 'create' ? t('Create Access Mode') : t('Edit Access Mode')}
            open={true}
            onOk={() => form.submit()}
            onCancel={onClose}
        >
            <Form<AccessModeValues>
                form={form}
                layout="vertical"
                initialValues={{
                    name: editAccessMode?.name,
                    description: editAccessMode?.description,
                    technical_asset_types: {
                        technical_asset_types: editAccessMode?.technical_asset_types ?? [],
                        default_for_technical_asset_types: editAccessMode?.default_for_technical_asset_types ?? [],
                    },
                }}
                onFinish={onFinish}
            >
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
                    extra={t(
                        'The default access mode of a Technical Asset type is preselected when creating a Technical Asset of that type.',
                    )}
                    required
                    rules={[
                        {
                            validator: async (_, value?: TechnicalAssetTypeSelection) => {
                                if (!value?.technical_asset_types.length) {
                                    throw new Error(
                                        t('Please provide at least one Technical Asset type for the access mode'),
                                    );
                                }
                            },
                        },
                    ]}
                >
                    <TechnicalAssetTypesTable
                        options={technicalAssetTypeOptions}
                        typesWithOtherDefault={typesWithOtherDefault}
                        lockedTypes={lockedTypes}
                        loading={isFetchingPlugins || isFetchingAccessModes}
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
