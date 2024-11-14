import { DataOutputLink, DatasetAccess, DatasetsGetContract } from '@/types/dataset';
import { TFunction } from 'i18next';
import { Popover, TableColumnsType } from 'antd';
import i18n from '@/i18n.ts';
import { getStatusLabel } from '@/utils/status.helper.ts';
import { TableStatusTag } from '@/components/list/table-status-tag/table-status-tag.component.tsx';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreaContract } from '@/types/business-area';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

const iconColumnWidth = 30;
export const getDatasetTableColumns = ({ t, datasets }: { t: TFunction, datasets: DatasetsGetContract }): TableColumnsType<DatasetsGetContract[0]> => {
    const sorter = new Sorter<DatasetsGetContract[0]>;
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: undefined,
            width: iconColumnWidth,
            dataIndex: 'access_type',
            render: (accessType: string) => {
                const isRestricted = accessType === 'restricted';
                return isRestricted ? (
                    <Popover content={t('Restricted access')} placement={'left'}>
                        <>
                            <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="x-small" color={'dark'} />
                        </>
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
            sorter: sorter.stringSorter(ds => ds.name),
            width: "20%"
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            render: (status) => {
                return <TableStatusTag status={status} />;
            },
            ...new FilterSettings(datasets, ds => getStatusLabel(ds.status)),
            sorter: sorter.stringSorter(ds => getStatusLabel(ds.status)),
            width: "12%"
        },
        {
            title: t('Business Area'),
            dataIndex: 'business_area',
            render: (businessArea: BusinessAreaContract) => {
                return <TableCellItem text={businessArea.name} />;
            },
            ellipsis: true,
            ...new FilterSettings(datasets, ds => ds.business_area.name),
            sorter: sorter.stringSorter(ds => ds.business_area.name),
            width: "13%"
        },
        {
            title: t('Access Type'),
            dataIndex: 'access_type',
            render: (accessType: DatasetAccess) => {
                return <TableCellItem text={getDatasetAccessTypeLabel(accessType)} />;
            },
            ellipsis: true,
            ...new FilterSettings(datasets, ds => getDatasetAccessTypeLabel(ds.access_type)),
            sorter: sorter.stringSorter(ds => getDatasetAccessTypeLabel(ds.access_type)),
            width: "15%"
        },
        {
            title: t('Produced by Data Product'),
            dataIndex: 'data_output_links',
            render: (data_output_links: DataOutputLink[]) => {
                console.log(data_output_links)
                if (data_output_links !== undefined) {
                    return <TableCellItem text={[... new Set(data_output_links.map(data_output_link =>
                        data_output_link.data_output.owner.name
                    ))].join(',')}/>;
                }
            },
            width: "25%"
            // ...new FilterSettings(datasets, ds => ds.business_area.name),
            // sorter: sorter.stringSorter(ds => ds.data_output_links.data_output.owner.name),
        },
        {
            title: t('Shared With'),
            dataIndex: 'data_product_count',
            render: (count: number) => {
                return <TableCellItem text={i18n.t('{{count}} data products', { count })} />;
            },
            sorter: sorter.numberSorter(ds => ds.data_product_count),
            width: "15%"
        },
    ]
};
