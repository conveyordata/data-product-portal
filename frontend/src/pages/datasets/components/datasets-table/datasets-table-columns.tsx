import { DatasetAccess, DatasetsGetContract } from '@/types/dataset';
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

const iconColumnWidth = 30;
export const getDatasetTableColumns = ({ t, datasets }: { t: TFunction, datasets: DatasetsGetContract }): TableColumnsType<DatasetsGetContract[0]> => [
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
        ...new FilterSettings(datasets, ds => ds.name),
    },
    {
        title: t('Status'),
        dataIndex: 'status',
        render: (status) => {
            return <TableStatusTag status={status} />;
        },
        ...new FilterSettings(datasets, ds => getStatusLabel(ds.status)),
    },
    {
        title: t('Business Area'),
        dataIndex: 'business_area',
        render: (businessArea: BusinessAreaContract) => {
            return <TableCellItem text={businessArea.name} />;
        },
        ellipsis: true,
        ...new FilterSettings(datasets, ds => ds.business_area.name),
    },
    {
        title: t('Access Type'),
        dataIndex: 'access_type',
        render: (accessType: DatasetAccess) => {
            return <TableCellItem text={getDatasetAccessTypeLabel(accessType)} />;
        },
        ellipsis: true,
        ...new FilterSettings(datasets, ds => getDatasetAccessTypeLabel(ds.access_type)),
    },
    {
        title: t('Shared With'),
        dataIndex: 'data_product_count',
        render: (count: number) => {
            return <TableCellItem text={i18n.t('{{count}} data products', { count })} />;
        },
    },
];
