import { Button, Flex, Popconfirm } from 'antd';
import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { Sorter } from '@/utils/table-sorter.helper';
import { DataProductSettingContract } from '@/types/data-product-setting';
import { ColumnType } from 'antd/es/table';

const iconColumnWidth = 30;
type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleOpen: (id: string) => void;
    onRemoveDataProductSetting: (id: string) => void;
};

export type EditableColumn = DataProductSettingContract & {
    editable: boolean;
};

interface EditableColumnType<T> extends ColumnType<T> {
    editable?: boolean;
}
export const getDataProductTableColumns = ({
    t,
    isDisabled,
    isLoading,
    onRemoveDataProductSetting,
}: Props): EditableColumnType<DataProductSettingContract>[] => {
    const sorter = new Sorter<DataProductSettingContract>();
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
            sorter: sorter.stringSorter((dp) => dp.name),
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
            sorter: sorter.stringSorter((dp) => dp.type),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Tooltip'),
            dataIndex: 'tooltip',
            ellipsis: {
                showTitle: false,
            },
            render: (tooltip: string) => <TableCellItem text={tooltip} tooltip={{ content: tooltip }} />,
            sorter: sorter.stringSorter((dp) => dp.tooltip),
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
            sorter: sorter.stringSorter((dp) => dp.divider),
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
            sorter: sorter.stringSorter((dp) => dp.default),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Order'),
            dataIndex: 'order',
            ellipsis: {
                showTitle: false,
            },
            render: (order: number) => <TableCellItem text={order.toString()} />,
            sorter: sorter.numberSorter((dp) => dp.order),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Scope'),
            dataIndex: 'scope',
            ellipsis: {
                showTitle: false,
            },
            render: (scope: string) => <TableCellItem text={t(scope)} />,
            sorter: sorter.stringSorter((dp) => dp.scope),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (_, { id }) => {
                return (
                    <Flex vertical>
                        <Popconfirm
                            title={t('Remove')}
                            description={t(
                                'Are you sure you want to delete the data product setting? This will remove the setting from all the data products',
                            )}
                            onConfirm={() => onRemoveDataProductSetting(id)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isLoading }}
                            autoAdjustOverflow={true}
                        >
                            <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
