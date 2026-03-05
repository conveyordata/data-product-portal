import {
    AlertOutlined,
    AuditOutlined,
    ClockCircleOutlined,
    RocketOutlined,
    ThunderboltOutlined,
} from '@ant-design/icons';
import { Badge, Button, Card, Flex, Space, Typography, theme } from 'antd';
import { type ReactNode, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import UnderConstruction from '@/components/empty/under-construction/under-construction.tsx';
import { PendingApprovalsInbox } from '@/pages/home/components/pending-approvals-inbox/pending-approvals-inbox.tsx';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';

const { Title, Text } = Typography;

type ActionCategory = 'pending-approvals' | 'health-alerts' | 'ready-to-build' | 'pending-requests';

interface CategoryConfig {
    key: ActionCategory;
    label: string;
    description: string;
    icon: ReactNode;
    accentColor: string;
    count: number;
    content: ReactNode;
}

export function ActionCenter() {
    const { token } = theme.useToken();
    const { t } = useTranslation();

    const { data: { pending_actions: pendingApprovals = [] } = {} } = useGetUserPendingActionsQuery();
    const healthAlerts = [];
    const readyToBuild = [];
    const pendingRequests = [];

    const categories: CategoryConfig[] = useMemo(
        () => [
            {
                key: 'pending-approvals' as ActionCategory,
                label: t('Pending Approvals'),
                description: t('Access requests awaiting your review'),
                icon: <AuditOutlined />,
                accentColor: '#6366f1',
                count: pendingApprovals.length,
                content: <PendingApprovalsInbox pendingApprovals={pendingApprovals} />,
            },
            {
                key: 'health-alerts' as ActionCategory,
                label: t('Health Alerts'),
                description: t('Quality issues with your products'),
                icon: <AlertOutlined />,
                accentColor: '#ef4444',
                count: healthAlerts.length,
                content: <UnderConstruction />,
            },
            {
                key: 'ready-to-build' as ActionCategory,
                label: t('Ready to Build'),
                description: t('Newly approved access to start using'),
                icon: <RocketOutlined />,
                accentColor: '#10b981',
                count: readyToBuild.length,
                content: <UnderConstruction />,
            },
            {
                key: 'pending-requests' as ActionCategory,
                label: 'Pending Requests',
                description: 'Your requests still being processed',
                icon: <ClockCircleOutlined />,
                accentColor: '#8b8fa3',
                count: pendingRequests.length,
                content: <UnderConstruction />,
            },
        ],
        [t, pendingApprovals, healthAlerts.length, pendingRequests.length, readyToBuild.length],
    );

    const totalActions = useMemo(() => categories.reduce((sum, cat) => sum + cat.count, 0), [categories]);

    const [selectedKey, setSelectedKey] = useState<ActionCategory | null>(null);

    const activeKey =
        selectedKey && categories.some((c) => c.key === selectedKey) ? selectedKey : (categories[0]?.key ?? null);

    const activeCategory = categories.find((c) => c.key === activeKey);

    return (
        <>
            <Space style={{ marginBottom: 20 }}>
                <ThunderboltOutlined style={{ fontSize: 20, color: token.colorPrimary }} />
                <Title level={3} style={{ margin: 0 }}>
                    {t('Action Center')}
                </Title>
                <Badge
                    count={totalActions}
                    overflowCount={99}
                    style={{
                        backgroundColor: token.colorPrimary,
                        boxShadow: 'none',
                    }}
                />
            </Space>

            <Flex gap={12}>
                {categories.map((cat) => {
                    const isActive = cat.key === activeKey;
                    return (
                        <Button
                            block
                            key={cat.key}
                            onClick={() => setSelectedKey(cat.key)}
                            style={{
                                flex: 1,
                                height: 'auto',
                                padding: '16px 20px',
                                borderStyle: 'solid',
                                borderWidth: isActive ? '2.0px' : '1.5px',
                                borderColor: isActive ? cat.accentColor : '#e8e8e8',
                                background: isActive ? `${cat.accentColor}08` : '#fff',
                                boxShadow: 'none',
                                whiteSpace: 'normal',
                            }}
                        >
                            <Space
                                vertical
                                align="start"
                                styles={{ root: { width: 'inherit' }, item: { width: 'inherit' } }}
                            >
                                <Flex
                                    justify={'space-between'}
                                    align={'center'}
                                    style={{
                                        marginBottom: 8,
                                        width: 'inherit',
                                    }}
                                >
                                    <div
                                        style={{
                                            width: 36,
                                            height: 36,
                                            borderRadius: 8,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            background: `${cat.accentColor}14`,
                                            color: cat.accentColor,
                                            fontSize: 18,
                                        }}
                                    >
                                        {cat.icon}
                                    </div>
                                    <Badge
                                        count={cat.count}
                                        style={{
                                            backgroundColor: cat.accentColor,
                                            boxShadow: 'none',
                                            fontSize: 11,
                                            fontWeight: 600,
                                        }}
                                    />
                                </Flex>
                                <Text
                                    strong
                                    style={{
                                        fontSize: 13,
                                        display: 'block',
                                        marginBottom: 2,
                                        color: isActive ? cat.accentColor : token.colorText,
                                        width: 'fit-content',
                                    }}
                                >
                                    {cat.label}
                                </Text>
                                <Text
                                    type="secondary"
                                    style={{ fontSize: 11, lineHeight: 1.3, display: 'block', width: 'fit-content' }}
                                >
                                    {cat.description}
                                </Text>
                            </Space>
                        </Button>
                    );
                })}
            </Flex>

            {/* Detail panel */}
            {activeCategory && (
                <Card
                    size="small"
                    style={{
                        marginTop: 16,
                        borderRadius: 10,
                        borderTop: `3px solid ${activeCategory.accentColor}`,
                    }}
                    styles={{
                        header: {
                            padding: '12px 20px',
                            minHeight: 0,
                            borderBottom: `1px solid ${token.colorBorderSecondary}`,
                        },
                        body: {
                            padding: 0,
                            maxHeight: 400,
                            overflowY: 'auto',
                        },
                    }}
                    title={
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <span style={{ color: activeCategory.accentColor, fontSize: 16 }}>
                                {activeCategory.icon}
                            </span>
                            <Text strong style={{ fontSize: 14 }}>
                                {activeCategory.label}
                            </Text>
                            <Badge
                                count={activeCategory.count}
                                size="small"
                                style={{
                                    backgroundColor: activeCategory.accentColor,
                                    boxShadow: 'none',
                                    fontSize: 10,
                                }}
                            />
                            <Text type="secondary" style={{ fontSize: 12, marginLeft: 'auto' }}>
                                {activeCategory.description}
                            </Text>
                        </div>
                    }
                >
                    {activeCategory.content}
                </Card>
            )}
        </>
    );
}
