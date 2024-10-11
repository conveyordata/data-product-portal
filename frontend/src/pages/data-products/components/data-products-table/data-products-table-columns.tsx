import { TableColumnsType } from 'antd';
import { DataProductsGetContract, DataProductStatus } from '@/types/data-product';
import { TeamOutlined } from '@ant-design/icons';
import i18n from '@/i18n';
import { TFunction } from 'i18next';
import { getStatusLabel } from '@/utils/status.helper.ts';
import { TableStatusTag } from '@/components/list/table-status-tag/table-status-tag.component.tsx';
import { DataProductTypeContract } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreaGetResponse } from '@/types/business-area';
import { FilterSettings } from '@/utils/table-filter.helper';

const iconColumnWidth = 30;
export const getDataProductTableColumns = ({ t, dataProducts: data }: { t: TFunction, dataProducts: DataProductsGetContract }): TableColumnsType<DataProductsGetContract[0]> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        // This is an empty column to match to give a small indentation to the table and match the datasets table icon column
        {
            title: undefined,
            width: iconColumnWidth,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            defaultSortOrder: 'ascend',
            ellipsis: {
                showTitle: false,
            },
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            render: (status: DataProductStatus) => {
                return <TableStatusTag status={status} />;
            },
            ...new FilterSettings(data, dp => getStatusLabel(dp.status))
        },
        {
            title: t('Business Area'),
            dataIndex: 'business_area',
            render: (businessArea: BusinessAreaGetResponse) => {
                return <TableCellItem text={businessArea.name} />;
            },
            ...new FilterSettings(data, dp => dp.business_area.name)
        },
        {
            title: t('Type'),
            dataIndex: 'type',
            render: (type: DataProductTypeContract) => {
                const icon = getDataProductTypeIcon(type.icon_key);
                return <TableCellItem reactSVGComponent={icon} text={type.name} />;
            },
            ellipsis: true,
            ...new FilterSettings(data, dp => dp.type.name)
        },
        {
            title: t('Access'),
            dataIndex: 'user_count',
            render: (userCount: number) => {
                return <TableCellItem icon={<TeamOutlined />} text={i18n.t('{{count}} users', { count: userCount })} />;
            },
        },
        {
            title: t('Consumes'),
            dataIndex: 'dataset_count',
            render: (datasetCount: number) => {
                return <TableCellItem text={i18n.t('{{count}} datasets', { count: datasetCount })} />;
            },
        },
    ];
};
