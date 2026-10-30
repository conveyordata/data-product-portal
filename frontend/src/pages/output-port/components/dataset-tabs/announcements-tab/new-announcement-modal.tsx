import { Alert, ConfigProvider, Flex, Form, Input, Modal, Select, Space, Typography, theme } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    AnnouncementTypeIcon,
    AnnouncementTypeLabel,
    getAnnouncementTypeConfig,
} from '@/components/announcements/announcement-type.tsx';
import {
    AnnouncementType,
    type CreateAnnouncement,
    useCreateOutputPortAnnouncementMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

const TITLE_MAX_LENGTH = 100;
const MESSAGE_MAX_LENGTH = 2000;

function CharacterCount({ length, max }: { length: number; max: number }) {
    return (
        <Flex justify="flex-end">
            <Typography.Text type="secondary">{`${length} / ${max}`}</Typography.Text>
        </Flex>
    );
}

type Props = {
    dataProductId: string;
    outputPortId: string;
    consumerCount: number;
    onClose: () => void;
};

export function NewAnnouncementModal({ dataProductId, outputPortId, consumerCount, onClose }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const [form] = Form.useForm<CreateAnnouncement>();
    const [createAnnouncement, { isLoading }] = useCreateOutputPortAnnouncementMutation();
    const typeConfig = getAnnouncementTypeConfig(t, token);
    const title = Form.useWatch('title', form) ?? '';
    const message = Form.useWatch('message', form) ?? '';

    const onFinish = async (values: CreateAnnouncement) => {
        try {
            await createAnnouncement({ dataProductId, id: outputPortId, createAnnouncement: values }).unwrap();
            dispatchMessage({ content: t('Announcement published'), type: 'success' });
            onClose();
        } catch (_error) {
            dispatchMessage({ content: t('Could not publish announcement'), type: 'error' });
        }
    };

    return (
        <Modal
            title={t('New Announcement')}
            open
            centered
            width={640}
            onCancel={onClose}
            onOk={() => form.submit()}
            confirmLoading={isLoading}
            okText={t('Publish')}
            cancelButtonProps={{ disabled: isLoading }}
        >
            <ConfigProvider theme={{ components: { Form: { itemMarginBottom: token.marginSM } } }}>
                <Form<CreateAnnouncement>
                    form={form}
                    layout="vertical"
                    initialValues={{ type: AnnouncementType.Info }}
                    onFinish={onFinish}
                    disabled={isLoading}
                >
                    <Form.Item<CreateAnnouncement>
                        label={t('Title')}
                        htmlFor="title"
                        required
                        tooltip={t('Pick the type with the icon in front of the title.')}
                        extra={<CharacterCount length={title.length} max={TITLE_MAX_LENGTH} />}
                    >
                        <Space.Compact block>
                            <Form.Item<CreateAnnouncement> name="type" noStyle rules={[{ required: true }]}>
                                <Select
                                    aria-label={t('Type')}
                                    style={{ width: 'auto' }}
                                    popupMatchSelectWidth={false}
                                    options={Object.values(AnnouncementType).map((type) => ({
                                        value: type,
                                        label: <AnnouncementTypeIcon type={type} />,
                                    }))}
                                    optionRender={({ data }) => (
                                        <Flex vertical>
                                            <AnnouncementTypeLabel type={data.value} />
                                            <Typography.Text type="secondary">
                                                {typeConfig[data.value].meaning}
                                            </Typography.Text>
                                        </Flex>
                                    )}
                                />
                            </Form.Item>
                            <Form.Item<CreateAnnouncement>
                                name="title"
                                noStyle
                                rules={[{ required: true, whitespace: true, message: t('Please provide a title') }]}
                            >
                                <Input
                                    id="title"
                                    placeholder={t('e.g. Version 2 is now available')}
                                    maxLength={TITLE_MAX_LENGTH}
                                />
                            </Form.Item>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item<CreateAnnouncement>
                        label={t('Message')}
                        htmlFor="message"
                        required
                        tooltip={t(
                            'Plain text. Say what happens, who is affected and what consumers need to do. Write any deadline or maintenance window here. Links starting with http:// or https:// become clickable.',
                        )}
                        extra={<CharacterCount length={message.length} max={MESSAGE_MAX_LENGTH} />}
                    >
                        <Form.Item<CreateAnnouncement>
                            name="message"
                            noStyle
                            rules={[{ required: true, whitespace: true, message: t('Please provide a message') }]}
                        >
                            <Input.TextArea rows={5} maxLength={MESSAGE_MAX_LENGTH} />
                        </Form.Item>
                    </Form.Item>
                </Form>
            </ConfigProvider>
            <Alert type="info" showIcon title={t('This will notify {{count}} consumers.', { count: consumerCount })} />
        </Modal>
    );
}
