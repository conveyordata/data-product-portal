import { TableColumnsType } from 'antd';
import { DataProductsGetContract, DataProductStatus } from '@/types/data-product';
import { TeamOutlined } from '@ant-design/icons';
import i18n from '@/i18n';
import { TFunction } from 'i18next';
import { TableStatusTag } from '@/components/list/table-status-tag/table-status-tag.component.tsx';
import { DataProductTypeContract } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreaGetResponse } from '@/types/business-area';

const iconColumnWidth = 30;
export const getDataProductTableColumns = ({ t }: { t: TFunction }): TableColumnsType<DataProductsGetContract[0]> => {
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
            filterSearch: true,
            defaultSortOrder: 'ascend',
            onFilter: (value, record) => record.name.startsWith(value as string),
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
        },
        {
            title: t('Business Area'),
            dataIndex: 'business_area',
            render: (businessArea: BusinessAreaGetResponse) => {
                return <TableCellItem text={businessArea.name} />;
            },
        },
        {
            title: t('Type'),
            dataIndex: 'type',
            filterSearch: true,
            onFilter: (value, record) => record.type.name.startsWith(value as string),
            render: (type: DataProductTypeContract) => {
                const icon = getDataProductTypeIcon(type.icon_key);
                return <TableCellItem reactSVGComponent={icon} text={type.name} />;
            },
            ellipsis: true,
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
        {
            title: t('Produces'),
            dataIndex: 'data_outputs_count',
            render: (dataOutputCount: number) => {
                return <TableCellItem text={i18n.t('{{count}} data outputs', { count: dataOutputCount })} />;
            },
        },
    ];
};
