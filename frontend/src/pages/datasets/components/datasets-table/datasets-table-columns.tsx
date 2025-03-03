import { Badge, Popover, TableColumnsType, Tag } from 'antd';
import type { TFunction } from 'i18next';

import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { DataOutputLink, DatasetAccess, DatasetsGetContract } from '@/types/dataset';
import { DatasetStatus } from '@/types/dataset/dataset.contract';
import { DomainContract } from '@/types/domain';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

import styles from './datasets-table.module.scss';

const iconColumnWidth = 30;

type Props = {
    t: TFunction;
    datasets: DatasetsGetContract;
};

export const getDatasetTableColumns = ({ t, datasets }: Props): TableColumnsType<DatasetsGetContract[0]> => {
    const sorter = new Sorter<DatasetsGetContract[0]>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: undefined,
            width: iconColumnWidth,
            dataIndex: 'status',
            render: (status: DatasetStatus) => {
                return (
                    <Popover content={getStatusLabel(t, status)} placement={'top'}>
                        <TableCellItem icon={<Badge status={getBadgeStatus(status)} />} />
                    </Popover>
                );
            },
        },
        {
            title: undefined,
            width: iconColumnWidth,
            dataIndex: 'access_type',
            render: (accessType: string) => {
                const isRestricted = accessType === 'restricted';
                return isRestricted ? (
                    <Popover content={t('Restricted access')} placement={'left'}>
                        <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="x-small" color={'dark'} />
                    </Popover>
                ) : null;
            },
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            defaultSortOrder: 'ascend',
            ellipsis: {
                showTitle: false,
            },
            render: (name: string) => {
                return <TableCellItem text={name} tooltip={{ content: name }} />;
            },
            sorter: sorter.stringSorter((ds) => ds.name),
            width: '20%',
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
            ...new FilterSettings(datasets, (dp) => (dp.lifecycle !== null ? dp.lifecycle.name : '')),
            sorter: sorter.stringSorter((dp) => (dp.lifecycle !== null ? dp.lifecycle.name : '')),
            width: '10%',
        },
        {
            title: t('Domain'),
            dataIndex: 'domain',
            render: (domain: DomainContract) => {
                return <TableCellItem text={domain.name} />;
            },
            ellipsis: true,
            ...new FilterSettings(datasets, (ds) => ds.domain.name),
            sorter: sorter.stringSorter((ds) => ds.domain.name),
            width: '13%',
        },
        {
            title: t('Access Type'),
            dataIndex: 'access_type',
            render: (accessType: DatasetAccess) => {
                return <TableCellItem text={getDatasetAccessTypeLabel(t, accessType)} />;
            },
            ellipsis: true,
            ...new FilterSettings(datasets, (ds) => getDatasetAccessTypeLabel(t, ds.access_type)),
            sorter: sorter.stringSorter((ds) => getDatasetAccessTypeLabel(t, ds.access_type)),
            width: '15%',
        },
        {
            title: t('Produced by Data Product'),
            dataIndex: 'data_output_links',
            render: (data_output_links: DataOutputLink[]) => {
                console.log(data_output_links);
                if (data_output_links !== undefined) {
                    return (
                        <TableCellItem
                            text={[
                                ...new Set(
                                    data_output_links.map(
                                        (data_output_link) => data_output_link.data_output.owner.name,
                                    ),
                                ),
                            ].join(',')}
                        />
                    );
                }
            },
            width: '25%',
            // ...new FilterSettings(datasets, ds => ds.domain.name),
            // sorter: sorter.stringSorter(ds => ds.data_output_links.data_output.owner.name),
        },
        {
            title: t('Shared With'),
            dataIndex: 'data_product_count',
            render: (count: number) => {
                return <TableCellItem text={t('{{count}} data products', { count })} />;
            },
            sorter: sorter.numberSorter((ds) => ds.data_product_count),
            width: '15%',
        },
    ];
};
