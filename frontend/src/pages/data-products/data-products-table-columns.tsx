import { TeamOutlined } from '@ant-design/icons';
import { Badge, Popover, type TableColumnsType, Tag } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type {
    DataProductLifeCycle,
    DataProductStatus,
    DataProductType,
    GetDataProductsResponseItem,
} from '@/store/api/services/generated/dataProductsApi.ts';
import type { DomainContract } from '@/types/domain';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';
import styles from './data-products-table.module.scss';

const iconColumnWidth = 30;
export const getDataProductTableColumns = ({
    t,
    dataProducts: data,
}: {
    t: TFunction;
    dataProducts: GetDataProductsResponseItem[];
}): TableColumnsType<GetDataProductsResponseItem> => {
    const sorter = new Sorter<GetDataProductsResponseItem>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        // This is an empty column to match to give a small indentation to the table and match the datasets table icon column
        {
            title: undefined,
            dataIndex: 'status',
            width: iconColumnWidth,
            render: (status: DataProductStatus) => {
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
            sorter: sorter.stringSorter((dp) => dp.name),
            defaultSortOrder: 'ascend',
            width: '25%',
        },
        {
            title: t('Status'),
            dataIndex: 'lifecycle',
            render: (lifecycle: DataProductLifeCycle) => {
                if (lifecycle !== null) {
                    return (
                        <Tag color={lifecycle.color || 'default'} className={styles.tag}>
                            {lifecycle.name}
                        </Tag>
                    );
                }
                return;
            },
            ...new FilterSettings(data, (dp) => (dp.lifecycle !== null ? dp.lifecycle.name : '')),
            sorter: sorter.stringSorter((dp) => (dp.lifecycle !== null ? dp.lifecycle.name : '')),
            width: '10%',
        },
        {
            title: t('Domain'),
            dataIndex: 'domain',
            render: (domain: DomainContract) => {
                return <TableCellItem text={domain.name} />;
            },
            ...new FilterSettings(data, (dp) => dp.domain.name),
            sorter: sorter.stringSorter((dp) => dp.domain.name),
        },
        {
            title: t('Type'),
            dataIndex: 'type',
            render: (type: DataProductType) => {
                const icon = getDataProductTypeIcon(type.icon_key);
                return <TableCellItem reactSVGComponent={icon} text={type.name} />;
            },
            ellipsis: true,
            ...new FilterSettings(data, (dp) => dp.type.name),
            sorter: sorter.stringSorter((dp) => dp.type.name),
        },
        {
            title: t('Team'),
            dataIndex: 'user_count',
            render: (userCount: number) => {
                return <TableCellItem icon={<TeamOutlined />} text={t('{{count}} members', { count: userCount })} />;
            },
            sorter: sorter.numberSorter((dp) => dp.user_count),
        },
        {
            title: t('Consumes'),
            dataIndex: 'dataset_count',
            render: (datasetCount: number) => {
                return <TableCellItem text={t('{{count}} Output Ports', { count: datasetCount })} />;
            },
            sorter: sorter.numberSorter((dp) => dp.output_port_count),
        },
        {
            title: t('Produces'),
            dataIndex: 'data_outputs_count',
            render: (dataOutputCount: number) => {
                return <TableCellItem text={t('{{count}} Technical Assets', { count: dataOutputCount })} />;
            },
        },
    ];
};
