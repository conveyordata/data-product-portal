import { Badge, Popover, TableColumnsType, Tag } from 'antd';
import { DataProductsGetContract, DataProductStatus } from '@/types/data-product';
import { TeamOutlined } from '@ant-design/icons';
import i18n from '@/i18n';
import { TFunction } from 'i18next';
import styles from './data-products-table.module.scss';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { DataProductTypeContract } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { DomainContract } from '@/types/domain';

const iconColumnWidth = 30;
export const getDataProductTableColumns = ({
    t,
    dataProducts: data,
}: {
    t: TFunction;
    dataProducts: DataProductsGetContract;
}): TableColumnsType<DataProductsGetContract[0]> => {
    const sorter = new Sorter<DataProductsGetContract[0]>();
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
                    <Popover content={getStatusLabel(status)} placement={'top'}>
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
            render: (lifecycle: DataProductLifeCycleContract) => {
                if (lifecycle !== null) {
                    return (
                        <Tag color={lifecycle.color || 'default'} className={styles.tag}>
                            {lifecycle.name}
                        </Tag>
                    );
                } else {
                    return;
                }
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
            render: (type: DataProductTypeContract) => {
                const icon = getDataProductTypeIcon(type.icon_key);
                return <TableCellItem reactSVGComponent={icon} text={type.name} />;
            },
            ellipsis: true,
            ...new FilterSettings(data, (dp) => dp.type.name),
            sorter: sorter.stringSorter((dp) => dp.type.name),
        },
        {
            title: t('Access'),
            dataIndex: 'user_count',
            render: (userCount: number) => {
                return <TableCellItem icon={<TeamOutlined />} text={i18n.t('{{count}} users', { count: userCount })} />;
            },
            sorter: sorter.numberSorter((dp) => dp.user_count),
        },
        {
            title: t('Consumes'),
            dataIndex: 'dataset_count',
            render: (datasetCount: number) => {
                return <TableCellItem text={i18n.t('{{count}} datasets', { count: datasetCount })} />;
            },
            sorter: sorter.numberSorter((dp) => dp.dataset_count),
        },
        {
            title: t('Produces'),
            dataIndex: 'data_outputs_count',
            render: (dataOutputCount: number) => {
                return <TableCellItem text={i18n.t('{{count}} data outputs', { count: dataOutputCount })} />;
            },
        },
    ];
};
