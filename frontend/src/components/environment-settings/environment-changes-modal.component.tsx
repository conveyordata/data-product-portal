import { ArrowRightOutlined, WarningOutlined } from '@ant-design/icons';
import { Card, Flex, Modal, Tag, Typography, theme } from 'antd';
import { useTranslation } from 'react-i18next';
import type { EnvironmentGetItem } from '@/store/api/services/generated/configurationEnvironmentsApi';
import type { EnvironmentChange } from './environment-settings.helper';

type Props = {
    open: boolean;
    environments: EnvironmentGetItem[];
    changes: Record<string, EnvironmentChange[]>;
    loading?: boolean;
    onConfirm: () => void;
    onCancel: () => void;
};

export function EnvironmentChangesModal({ open, environments, changes, loading, onConfirm, onCancel }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    return (
        <Modal
            open={open}
            title={t('Save Environment Settings?')}
            width={560}
            okText={t('Save Changes')}
            cancelText={t('Cancel')}
            confirmLoading={loading}
            onOk={onConfirm}
            onCancel={onCancel}
        >
            <Flex vertical gap="middle">
                <Typography.Text>{t('Only Environments you changed are updated.')}</Typography.Text>
                {environments.map((environment) => {
                    const items = changes[environment.id] ?? [];
                    return (
                        <Card
                            key={environment.id}
                            size="small"
                            type="inner"
                            style={{ borderColor: token.colorBorder }}
                            data-testid={`changes-${environment.acronym}`}
                            title={
                                <Typography.Text strong>
                                    {environment.acronym}{' '}
                                    <Typography.Text type="secondary">{environment.name}</Typography.Text>
                                </Typography.Text>
                            }
                            extra={
                                items.length > 0 && (
                                    <Tag color="warning" icon={<WarningOutlined />}>
                                        {t('Will be updated')}
                                    </Tag>
                                )
                            }
                        >
                            {items.length > 0 ? (
                                <Flex vertical gap="small">
                                    {items.map((item) => (
                                        <Flex key={item.field} justify="space-between" gap="middle">
                                            <Typography.Text>{item.label}</Typography.Text>
                                            <Flex gap="small" align="center">
                                                <Typography.Text type="secondary" delete>
                                                    {item.from}
                                                </Typography.Text>
                                                <ArrowRightOutlined />
                                                <Typography.Text strong>{item.to}</Typography.Text>
                                            </Flex>
                                        </Flex>
                                    ))}
                                </Flex>
                            ) : (
                                <Typography.Text type="secondary">
                                    {t('No changes. This Environment is not reprovisioned.')}
                                </Typography.Text>
                            )}
                        </Card>
                    );
                })}
            </Flex>
        </Modal>
    );
}
