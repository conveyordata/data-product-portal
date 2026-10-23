import { Form, Input, Modal, Select } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type PlatformType,
    PlatformTypeKind,
    useGetAllPlatformsQuery,
} from '@/store/api/services/generated/configurationPlatformsApi.ts';
import { useCreateToolMutation } from '@/store/api/services/generated/dataProductsToolsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    dataProductId: string;
    onClose: () => void;
};

type CreateToolValues = {
    type: string;
    name: string;
    description: string;
    base_values: Record<string, string>;
};

const TYPE_SEPARATOR = '/';

export function CreateToolModal({ dataProductId, onClose }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm<CreateToolValues>();
    const selectedType = Form.useWatch('type', form);
    const { data: { platforms = [] } = {}, isFetching } = useGetAllPlatformsQuery();
    const [createTool, { isLoading }] = useCreateToolMutation();

    const toolTypes = useMemo(() => {
        const types = new Map<string, { platformKey: string; type: PlatformType }>();
        for (const platform of platforms) {
            for (const type of platform.types) {
                if (type.kind === PlatformTypeKind.Tool) {
                    types.set(`${platform.key}${TYPE_SEPARATOR}${type.name}`, { platformKey: platform.key, type });
                }
            }
        }
        return types;
    }, [platforms]);

    const typeOptions = platforms
        .filter((platform) => platform.types.some((type) => type.kind === PlatformTypeKind.Tool))
        .map((platform) => ({
            label: platform.display_name,
            options: platform.types
                .filter((type) => type.kind === PlatformTypeKind.Tool)
                .map((type) => ({ label: type.display_name, value: `${platform.key}${TYPE_SEPARATOR}${type.name}` })),
        }));

    const selected = selectedType ? toolTypes.get(selectedType) : undefined;

    const onFinish = async (values: CreateToolValues) => {
        if (!selected) {
            return;
        }
        await createTool({
            dataProductId,
            createToolRequest: {
                name: values.name,
                description: values.description ?? '',
                platform_key: selected.platformKey,
                tool_type: selected.type.name,
                base_values: values.base_values ?? {},
            },
        }).unwrap();
        dispatchMessage({ content: t('Tool created successfully'), type: 'success' });
        onClose();
    };

    return (
        <Modal
            centered
            open
            title={t('Create Tool')}
            okText={t('Create')}
            onOk={() => form.submit()}
            onCancel={onClose}
            okButtonProps={{ loading: isLoading }}
        >
            <Form<CreateToolValues> form={form} layout="vertical" onFinish={onFinish}>
                <Form.Item<CreateToolValues>
                    name="type"
                    label={t('Tool type')}
                    rules={[{ required: true, message: t('Please select a Tool type') }]}
                >
                    <Select
                        loading={isFetching}
                        options={typeOptions}
                        onChange={() => form.resetFields(['base_values'])}
                    />
                </Form.Item>
                <Form.Item<CreateToolValues>
                    name="name"
                    label={t('Name')}
                    rules={[{ required: true, message: t('Please provide the name of the Tool') }]}
                >
                    <Input />
                </Form.Item>
                <Form.Item<CreateToolValues> name="description" label={t('Description')}>
                    <Input.TextArea rows={3} />
                </Form.Item>
                {selected?.type.overridable_properties?.map((property) => (
                    <Form.Item
                        key={`${selectedType}-${property.name}`}
                        name={['base_values', property.name]}
                        label={property.label}
                        initialValue={property.default}
                    >
                        <Select options={property.allowed_values.map((value) => ({ label: value, value }))} />
                    </Form.Item>
                ))}
            </Form>
        </Modal>
    );
}
