import { Button, Flex, Popconfirm, TableColumnsType } from 'antd';
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
import { Sorter } from '@/utils/table-sorter.helper';
import { DataProductSettingContract } from '@/types/data-product-setting';

const iconColumnWidth = 30;
type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleOpen: (id: string) => void;
    onRemoveDataProductSetting: (id: string) => void;
}

export const getDataProductTableColumns = ({
    t,
    isDisabled,
    isLoading,
    onRemoveDataProductSetting,
}: Props): TableColumnsType<DataProductSettingContract&{editable: boolean}> => {
    const sorter = new Sorter<DataProductSettingContract>;
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
            ellipsis: {
            showTitle: false,
            },
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            sorter: sorter.stringSorter(dp => dp.name),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Type'),
            dataIndex: 'type',
            ellipsis: {
            showTitle: false,
            },
            render: (type: string) => <TableCellItem text={type} />,
            sorter: sorter.stringSorter(dp => dp.type),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Tooltip'),
            dataIndex: 'tooltip',
            ellipsis: {
            showTitle: false,
            },
            render: (tooltip: string) => <TableCellItem text={tooltip} tooltip={{content: tooltip}}/>,
            sorter: sorter.stringSorter(dp => dp.tooltip),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Divider'),
            dataIndex: 'divider',
            ellipsis: {
            showTitle: false,
            },
            render: (divider: string) => <TableCellItem text={divider} />,
            sorter: sorter.stringSorter(dp => dp.divider),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Default'),
            dataIndex: 'default',
            ellipsis: {
            showTitle: false,
            },
            render: (defaultVal: string) => <TableCellItem text={defaultVal} />,
            sorter: sorter.stringSorter(dp => dp.default),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Order'),
            dataIndex: 'order',
            ellipsis: {
            showTitle: false,
            },
            render: (order: number) => <TableCellItem text={order} />,
            sorter: sorter.stringSorter(dp => dp.order),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        // {
        //     title: t('Status'),
        //     dataIndex: 'status',
        //     render: (status: DataProductStatus) => {
        //         return <TableStatusTag status={status} />;
        //     },
        //     ...new FilterSettings(data, dp => getStatusLabel(dp.status)),
        //     sorter: sorter.stringSorter(dp => getStatusLabel(dp.status)),
        // },
        // {
        //     title: t('Business Area'),
        //     dataIndex: 'business_area',
        //     render: (businessArea: BusinessAreaGetResponse) => {
        //         return <TableCellItem text={businessArea.name} />;
        //     },
        //     ...new FilterSettings(data, dp => dp.business_area.name),
        //     sorter: sorter.stringSorter(dp => dp.business_area.name),
        // },
        // {
        //     title: t('Type'),
        //     dataIndex: 'type',
        //     render: (type: DataProductTypeContract) => {
        //         const icon = getDataProductTypeIcon(type.icon_key);
        //         return <TableCellItem reactSVGComponent={icon} text={type.name} />;
        //     },
        //     ellipsis: true,
        //     ...new FilterSettings(data, dp => dp.type.name),
        //     sorter: sorter.stringSorter(dp => dp.type.name),
        // },
        // {
        //     title: t('Access'),
        //     dataIndex: 'user_count',
        //     render: (userCount: number) => {
        //         return <TableCellItem icon={<TeamOutlined />} text={i18n.t('{{count}} users', { count: userCount })} />;
        //     },
        //     sorter: sorter.numberSorter(dp => dp.user_count),
        // },
        // {
        //     title: t('Consumes'),
        //     dataIndex: 'dataset_count',
        //     render: (datasetCount: number) => {
        //         return <TableCellItem text={i18n.t('{{count}} datasets', { count: datasetCount })} />;
        //     },
        //     sorter: sorter.numberSorter(dp => dp.dataset_count),
        // },
        // {
        //     title: t('Produces'),
        //     dataIndex: 'data_outputs_count',
        //     render: (dataOutputCount: number) => {
        //         return <TableCellItem text={i18n.t('{{count}} data outputs', { count: dataOutputCount })} />;
        //     },
        // },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (_, { id }) => {
                return (
                    <Flex vertical>
                    <Popconfirm
                        title={t('Remove')}
                        description={t('Are you sure you want to delete the data product setting? This will remove the setting from all the data products')}
                        onConfirm={() => onRemoveDataProductSetting(id)}
                        placement={'leftTop'}
                        okText={t('Confirm')}
                        cancelText={t('Cancel')}
                        okButtonProps={{ loading: isLoading }}
                        autoAdjustOverflow={true}
                    >
                    <Button
                        loading={isLoading}
                        disabled={isLoading || isDisabled}
                        type={'link'}
                    >
                        {t('Remove')}
                    </Button>
                    </Popconfirm>
                    </Flex>
                );
            },
          },
    ];
};
