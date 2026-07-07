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
    useUpdateAccessDurationMutation,
} from '@/store/api/services/generated/accessDurationsApi';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';

type ConsumerPolicy = {
    key: AbstractDataProductType;
    durationType: AccessDurationType;
    defaultDays: number | null;
    alternativeAllowed: boolean;
    alternativeDays?: number;
    defaultId: string;
    alternativeId?: string;
};

const PRODUCT_TYPE_LABELS: Record<string, string> = {
    [AbstractDataProductType.DataProducts]: 'Data Products',
    [AbstractDataProductType.Explorations]: 'Explorations',
};

function toPolicies(durations: AccessDuration[]): ConsumerPolicy[] {
    const byType = durations.reduce<Partial<Record<AbstractDataProductType, AccessDuration[]>>>((acc, d) => {
        const existing = acc[d.abstract_data_product_type];
        acc[d.abstract_data_product_type] = existing ? [...existing, d] : [d];
        return acc;
    }, {});

    return (Object.entries(byType) as [AbstractDataProductType, AccessDuration[]][]).map(([type, rows]) => {
        const defaultRow = rows.find((r) => r.is_default) ?? rows[0];
        const alternativeRow = rows.find((r) => !r.is_default);
        return {
            key: type,
            durationType: defaultRow.access_duration_type,
            defaultDays: defaultRow.days,
            alternativeAllowed: !!alternativeRow,
            alternativeDays: alternativeRow?.days ?? undefined,
            defaultId: defaultRow.id,
            alternativeId: alternativeRow?.id,
        };
    });
}

export function AccessPolicyTab() {
    const { t } = useTranslation();
    const { data: accessDurations } = useGetAllAccessDurationsQuery();
    const [policies, setPolicies] = useState<ConsumerPolicy[]>([]);
    const [updateAccessDuration] = useUpdateAccessDurationMutation();

    useEffect(() => {
        if (accessDurations) setPolicies(toPolicies(accessDurations));
    }, [accessDurations]);

    const updatePolicy = (key: AbstractDataProductType, patch: Partial<ConsumerPolicy>) => {
        setPolicies((prev) => prev.map((p) => (p.key === key ? { ...p, ...patch } : p)));
    };

    const handleSave = async () => {
        try {
            await Promise.all(
                policies.map((policy) =>
                    updateAccessDuration({
                        abstractDataProductType: policy.key,
                        accessDurationUpdate: {
                            access_duration_type: policy.durationType,
                            days: policy.defaultDays,
                            alternative_allowed: policy.alternativeAllowed,
                            alternative_days: policy.alternativeDays ?? null,
                        },
                    }).unwrap(),
                ),
            );
            dispatchMessage({ content: t('Access duration settings saved successfully'), type: 'success' });
        } catch (_e) {
            dispatchMessage({ content: t('Failed to save access duration settings'), type: 'error' });
        }
    };

    const columns: TableColumnsType<ConsumerPolicy> = [
        {
            title: t('Consumer type'),
            key: 'consumer_type',
            width: 200,
            render: (_, record) => (
                <Flex align="center" gap={'small'}>
                    <AbstractProductIcon type={record.key} />
                    <Typography.Text strong>{t(PRODUCT_TYPE_LABELS[record.key] ?? record.key)}</Typography.Text>
                </Flex>
            ),
        },
        {
            title: (
                <Flex align="center" gap={'small'}>
                    {t('Default duration')}
                    <Tooltip title={t('The default access duration assigned when a request is approved.')}>
                        <InfoCircleOutlined style={{ color: 'var(--ant-color-text-secondary)', cursor: 'help' }} />
                    </Tooltip>
                </Flex>
            ),
            key: 'duration',
            width: 320,
            render: (_, record) => (
                <Flex align="center" gap={'small'}>
                    <Select
                        value={record.durationType}
                        onChange={(val: AccessDurationType) =>
                            updatePolicy(record.key, {
                                durationType: val,
                                defaultDays: val === AccessDurationType.TimeBound ? (record.defaultDays ?? 30) : null,
                            })
                        }
                        options={[
                            { label: t('Permanent'), value: AccessDurationType.Permanent },
                            { label: t('Time-bound'), value: AccessDurationType.TimeBound },
                        ]}
                    />
                    {record.durationType === AccessDurationType.TimeBound && (
                        <InputNumber
                            min={1}
                            value={record.defaultDays ?? undefined}
                            onChange={(val) => updatePolicy(record.key, { defaultDays: val ?? 1 })}
                            addonAfter={t('days')}
                        />
                    )}
                </Flex>
            ),
        },
        {
            title: (
                <Flex align="center" gap={'small'}>
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
                const isTimeBound = record.durationType === AccessDurationType.TimeBound;
                const label = isTimeBound ? t('Permanent allowed') : t('Time-bound allowed');

                return (
                    <Flex align="center" gap={'small'}>
                        <Checkbox
                            checked={record.alternativeAllowed}
                            onChange={(e) => {
                                const checked = e.target.checked;
                                const alternativeIsTimeBound = record.durationType === AccessDurationType.Permanent;
                                const alternativeDays =
                                    checked && alternativeIsTimeBound ? (record.alternativeDays ?? 30) : undefined;
                                updatePolicy(record.key, { alternativeAllowed: checked, alternativeDays });
                            }}
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
        <Flex vertical gap={'small'}>
            <Flex vertical gap={'small'}>
                <Typography.Title level={3}>{t('Access Duration Settings')}</Typography.Title>
                <Typography.Text type="secondary">
                    {t('Configure default access durations for Explorations and Data Products.')}
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
