import { InfoCircleOutlined } from '@ant-design/icons';
import { Button, Checkbox, Flex, InputNumber, Select, Table, type TableColumnsType, Tooltip, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductOutlined, ExplorationOutlined } from '@/components/icons/index.tsx';

type DurationType = 'permanent' | 'time_bound';

type ConsumerPolicy = {
    key: string;
    label: string;
    icon: React.ReactNode;
    durationType: DurationType;
    defaultDays: number;
    alternativeAllowed: boolean;
    alternativeDays: number;
};

const DEFAULT_POLICIES: ConsumerPolicy[] = [
    {
        key: 'data_products',
        label: 'Data Products',
        icon: <DataProductOutlined />,
        durationType: 'permanent',
        defaultDays: 90,
        alternativeAllowed: false,
        alternativeDays: 90,
    },
    {
        key: 'explorations',
        label: 'Explorations',
        icon: <ExplorationOutlined />,
        durationType: 'time_bound',
        defaultDays: 30,
        alternativeAllowed: true,
        alternativeDays: 30,
    },
];

export function AccessPolicyForm() {
    const { t } = useTranslation();
    const [policies, setPolicies] = useState<ConsumerPolicy[]>(DEFAULT_POLICIES);

    const updatePolicy = (key: string, patch: Partial<ConsumerPolicy>) => {
        setPolicies((prev) => prev.map((p) => (p.key === key ? { ...p, ...patch } : p)));
    };

    const handleSave = () => {
        // TODO: persist via API
    };

    const columns: TableColumnsType<ConsumerPolicy> = [
        {
            title: t('Consumer type'),
            dataIndex: 'label',
            key: 'label',
            width: 200,
            render: (label: string, record) => (
                <Flex align="center" gap={8}>
                    {record.icon}
                    <Typography.Text strong>{t(label)}</Typography.Text>
                </Flex>
            ),
        },
        {
            title: (
                <Flex align="center" gap={6}>
                    {t('Default duration')}
                    <Tooltip title={t('The default access duration assigned when a request is approved.')}>
                        <InfoCircleOutlined style={{ color: 'var(--ant-color-text-secondary)', cursor: 'help' }} />
                    </Tooltip>
                </Flex>
            ),
            key: 'duration',
            width: 320,
            render: (_, record) => (
                <Flex align="center" gap={12}>
                    <Select
                        value={record.durationType}
                        onChange={(val: DurationType) => updatePolicy(record.key, { durationType: val })}
                        options={[
                            { label: t('Permanent'), value: 'permanent' },
                            { label: t('Time-bound'), value: 'time_bound' },
                        ]}
                    />
                    {record.durationType === 'time_bound' && (
                        <InputNumber
                            min={1}
                            value={record.defaultDays}
                            onChange={(val) => updatePolicy(record.key, { defaultDays: val ?? 1 })}
                            addonAfter={t('days')}
                        />
                    )}
                </Flex>
            ),
        },
        {
            title: (
                <Flex align="center" gap={6}>
                    {t('Alternative allowed')}
                    <Tooltip
                        title={t(
                            'Whether requesters can ask for an alternative duration (e.g. permanent when default is time-bound, or vice versa).',
                        )}
                    >
                        <InfoCircleOutlined style={{ color: 'var(--ant-color-text-secondary)', cursor: 'help' }} />
                    </Tooltip>
                </Flex>
            ),
            key: 'alternative',
            width: 360,
            render: (_, record) => {
                const isTimeBound = record.durationType === 'time_bound';
                const label = isTimeBound ? t('Permanent allowed') : t('Time-bound allowed');

                return (
                    <Flex align="center" gap={12}>
                        <Checkbox
                            checked={record.alternativeAllowed}
                            onChange={(e) => updatePolicy(record.key, { alternativeAllowed: e.target.checked })}
                        />
                        <Typography.Text>{label}</Typography.Text>
                        {!isTimeBound && record.alternativeAllowed && (
                            <InputNumber
                                min={1}
                                value={record.alternativeDays}
                                onChange={(val) => updatePolicy(record.key, { alternativeDays: val ?? 1 })}
                                addonAfter={t('days')}
                            />
                        )}
                    </Flex>
                );
            },
        },
    ];

    return (
        <Flex vertical gap={10}>
            <Flex vertical gap={4}>
                <Typography.Title level={3}>{t('Access Duration Settings')}</Typography.Title>
                <Typography.Text type="secondary">
                    {t('Configure default access durations for explorations and data products.')}
                </Typography.Text>
            </Flex>
            <Table<ConsumerPolicy>
                columns={columns}
                dataSource={policies}
                rowKey="key"
                pagination={false}
                tableLayout="fixed"
            />
            <div>
                <Button type="primary" onClick={handleSave}>
                    {t('Save')}
                </Button>
            </div>
        </Flex>
    );
}
