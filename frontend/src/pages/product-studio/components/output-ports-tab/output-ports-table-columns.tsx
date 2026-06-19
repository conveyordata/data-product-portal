import { Badge, Popover, type TableColumnsType, Tag } from 'antd';
import type { TFunction } from 'i18next';
import { ConsumersIcon } from '@/components/icons';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { QualityBadge } from '@/components/quality-badge/quality-badge.component';
import { DataQualityStatus } from '@/store/api/services/generated/dataProductsOutputPortsDataQualityApi';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

const iconColumnWidth = 30;

export const getOutputPortTableColumns = ({
    t,
    outputPorts: data,
}: {
    t: TFunction;
    outputPorts: SearchOutputPortsResponseItem[];
}): TableColumnsType<SearchOutputPortsResponseItem> => {
    const sorter = new Sorter<SearchOutputPortsResponseItem>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        // Status indicator column
        {
            title: undefined,
            dataIndex: 'status',
            width: iconColumnWidth,
            render: (status) => {
                return (
                    <Popover content={getStatusLabel(t, status)} placement={'top'}>
                        <TableCellItem icon={<Badge status={getBadgeStatus(status)} />} />
                    </Popover>
                );
            },
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: {
                showTitle: false,
            },
            render: (name) => {
                return <TableCellItem text={name} tooltip={{ content: name }} />;
            },
            sorter: sorter.stringSorter((op) => op.name),
            defaultSortOrder: 'ascend',
            width: '20%',
        },
        {
            title: t('Data Product'),
            dataIndex: 'data_product_name',
            render: (dataProductName: string) => {
                return <TableCellItem text={dataProductName} />;
            },
            ...new FilterSettings(data, (op) => op.data_product_name),
            sorter: sorter.stringSorter((op) => op.data_product_name),
            width: '15%',
        },
        {
            title: t('Status'),
            dataIndex: 'lifecycle',
            render: (lifecycle) => {
                if (lifecycle !== null) {
                    return <Tag color={lifecycle.color || 'default'}>{lifecycle.name}</Tag>;
                }
                return;
            },
            ...new FilterSettings(data, (op) => (op.lifecycle !== null ? op.lifecycle.name : '')),
            sorter: sorter.stringSorter((op) => (op.lifecycle !== null ? op.lifecycle.name : '')),
            width: '10%',
        },
        {
            title: t('Access Type'),
            dataIndex: 'access_type',
            render: (accessType: string) => {
                return <Tag>{accessType}</Tag>;
            },
            ...new FilterSettings(data, (op) => op.access_type),
            sorter: sorter.stringSorter((op) => op.access_type),
            width: '10%',
        },
        {
            title: t('Consumers'),
            dataIndex: 'abstract_data_product_count',
            render: (count: number) => {
                if (count === 0) {
                    return <TableCellItem text={t('No consumers yet')} />;
                }
                return <TableCellItem icon={<ConsumersIcon />} text={t('{{count}} consumers', { count })} />;
            },
            sorter: sorter.numberSorter((op) => op.abstract_data_product_count),
        },
        {
            title: t('Quality'),
            dataIndex: 'quality_status',
            render: (quality_status?: DataQualityStatus) => (
                <QualityBadge quality_status={quality_status ?? DataQualityStatus.Unknown} />
            ),
            width: '10%',
        },
    ];
};
