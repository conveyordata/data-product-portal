import { Flex, Progress, Segmented, Statistic, Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDataProductCostSummaryQuery } from '@/store/api/services/generated/dataProductsApi.ts';

type Props = {
    dataProductId: string;
};

type BreakdownRow = {
    output_port_id: string;
    output_port_name: string;
    compute_cost: number;
    storage_cost: number;
    platform_overhead_cost: number;
    total_cost: number;
    share: number;
};

function formatEur(value: number): string {
    return `€${value.toFixed(2)}`;
}

export function CostsTab({ dataProductId }: Props) {
    const { t } = useTranslation();

    const DAY_RANGE_OPTIONS = [
        { label: t('Last 30 days'), value: 30 },
        { label: t('Last 90 days'), value: 90 },
        { label: t('Last 180 days'), value: 180 },
    ];
    const [dayRange, setDayRange] = useState<number>(30);

    const { data, isLoading } = useGetDataProductCostSummaryQuery(
        { id: dataProductId, dayRange },
        { skip: !dataProductId },
    );

    const totalCost = Number(data?.total_cost ?? 0);

    const tableData: BreakdownRow[] = (data?.breakdown ?? []).map((item) => ({
        output_port_id: item.output_port_id,
        output_port_name: item.output_port_name,
        compute_cost: Number(item.compute_cost),
        storage_cost: Number(item.storage_cost),
        platform_overhead_cost: Number(item.platform_overhead_cost),
        total_cost: Number(item.total_cost),
        share: totalCost > 0 ? (Number(item.total_cost) / totalCost) * 100 : 0,
    }));

    const columns: ColumnsType<BreakdownRow> = [
        {
            title: t('Output Port'),
            dataIndex: 'output_port_name',
            key: 'output_port_name',
        },
        {
            title: t('Compute'),
            dataIndex: 'compute_cost',
            key: 'compute_cost',
            align: 'right',
            render: (v: number) => formatEur(v),
        },
        {
            title: t('Storage'),
            dataIndex: 'storage_cost',
            key: 'storage_cost',
            align: 'right',
            render: (v: number) => formatEur(v),
        },
        {
            title: t('Platform Overhead'),
            dataIndex: 'platform_overhead_cost',
            key: 'platform_overhead_cost',
            align: 'right',
            render: (v: number) => formatEur(v),
        },
        {
            title: t('Total'),
            dataIndex: 'total_cost',
            key: 'total_cost',
            align: 'right',
            render: (v: number) => <strong>{formatEur(v)}</strong>,
        },
        {
            title: t('Share'),
            dataIndex: 'share',
            key: 'share',
            render: (share: number) => (
                <Progress percent={Math.round(share)} showInfo={false} size="small" style={{ width: 100 }} />
            ),
        },
    ];

    const summaryRow = () => (
        <Table.Summary.Row>
            <Table.Summary.Cell index={0}>
                <strong>{t('Total')}</strong>
            </Table.Summary.Cell>
            <Table.Summary.Cell index={1} align="right">
                {formatEur(tableData.reduce((s, r) => s + r.compute_cost, 0))}
            </Table.Summary.Cell>
            <Table.Summary.Cell index={2} align="right">
                {formatEur(tableData.reduce((s, r) => s + r.storage_cost, 0))}
            </Table.Summary.Cell>
            <Table.Summary.Cell index={3} align="right">
                {formatEur(tableData.reduce((s, r) => s + r.platform_overhead_cost, 0))}
            </Table.Summary.Cell>
            <Table.Summary.Cell index={4} align="right">
                <strong>{formatEur(totalCost)}</strong>
            </Table.Summary.Cell>
            <Table.Summary.Cell index={5} />
        </Table.Summary.Row>
    );

    return (
        <Flex vertical gap="large">
            <Segmented options={DAY_RANGE_OPTIONS} value={dayRange} onChange={(v) => setDayRange(v as number)} />

            <Statistic title={t('Total Cost')} value={isLoading ? '—' : formatEur(totalCost)} />

            <Table<BreakdownRow>
                dataSource={tableData}
                columns={columns}
                rowKey="output_port_id"
                loading={isLoading}
                pagination={false}
                summary={tableData.length > 0 ? summaryRow : undefined}
                locale={{ emptyText: t('No cost data available for this period') }}
            />
        </Flex>
    );
}
