import { InfoCircleOutlined } from '@ant-design/icons';
import { Button, Checkbox, Flex, InputNumber, Select, Table, type TableColumnsType, Tooltip, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AbstractProductIcon } from '@/components/icons/index.tsx';
import {
    AbstractDataProductType,
    type AccessDuration,
    AccessDurationType,
    useGetAllAccessDurationsQuery,
} from '@/store/api/services/generated/accessDurationsApi';

const PRODUCT_TYPE_LABELS: Record<string, string> = {
    [AbstractDataProductType.DataProducts]: 'Data Products',
    [AbstractDataProductType.Explorations]: 'Explorations',
};

export function AccessPolicyForm() {
    const { t } = useTranslation();
    const { data: accessDurations } = useGetAllAccessDurationsQuery();
    const [policies, setPolicies] = useState<AccessDuration[]>([]);

    useEffect(() => {
        if (accessDurations) setPolicies(accessDurations);
    }, [accessDurations]);

    const updatePolicy = (id: string, patch: Partial<AccessDuration>) => {
        setPolicies((prev) => prev.map((p) => (p.id === id ? { ...p, ...patch } : p)));
    };

    const handleSave = () => {
        // TODO: persist via API
    };

    const columns: TableColumnsType<AccessDuration> = [
        {
            title: t('Consumer type'),
            dataIndex: 'abstract_data_product_type',
            key: 'abstract_data_product_type',
            width: 200,
            render: (type: AbstractDataProductType) => (
                <Flex align="center" gap={8}>
                    <AbstractProductIcon type={type} />
                    <Typography.Text strong>{t(PRODUCT_TYPE_LABELS[type] ?? type)}</Typography.Text>
                </Flex>
            ),
        },
        {
            title: (
                <Flex align="center" gap={6}>
                    {t('Duration type')}
                    <Tooltip title={t('The access duration assigned when a request is approved.')}>
                        <InfoCircleOutlined style={{ color: 'var(--ant-color-text-secondary)', cursor: 'help' }} />
                    </Tooltip>
                </Flex>
            ),
            key: 'duration',
            dataIndex: 'access_duration_type',
            width: 320,
            render: (_, record) => (
                <Flex align="center" gap={12}>
                    <Select
                        value={record.access_duration_type}
                        onChange={(val) => updatePolicy(record.id, { access_duration_type: val })}
                        options={[
                            { label: t('Permanent'), value: AccessDurationType.Permanent },
                            { label: t('Time-bound'), value: AccessDurationType.TimeBound },
                        ]}
                    />
                    {record.access_duration_type === AccessDurationType.TimeBound && (
                        <InputNumber
                            min={1}
                            value={record.days ?? undefined}
                            onChange={(val) => updatePolicy(record.id, { days: val ?? 1 })}
                            addonAfter={t('days')}
                        />
                    )}
                </Flex>
            ),
        },
        {
            title: (
                <Flex align="center" gap={6}>
                    {t('Is default')}
                    <Tooltip title={t('Whether this is the default duration type for the consumer type.')}>
                        <InfoCircleOutlined style={{ color: 'var(--ant-color-text-secondary)', cursor: 'help' }} />
                    </Tooltip>
                </Flex>
            ),
            key: 'is_default',
            width: 200,
            render: (_, record) => (
                <Checkbox
                    checked={record.is_default}
                    onChange={(e) => updatePolicy(record.id, { is_default: e.target.checked })}
                />
            ),
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
            <Table<AccessDuration>
                columns={columns}
                dataSource={policies}
                rowKey="id"
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
