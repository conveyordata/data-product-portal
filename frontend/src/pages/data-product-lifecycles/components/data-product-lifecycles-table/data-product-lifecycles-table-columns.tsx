import { Button, Checkbox, ColorPicker, Flex, Popconfirm } from 'antd';
import { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { Sorter } from '@/utils/table-sorter.helper';
import { DataProductSettingContract } from '@/types/data-product-setting';
import { ColumnType } from 'antd/es/table';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';

const iconColumnWidth = 30;
type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleOpen: (id: string) => void;
    editColor: (record: DataProductLifeCycleContract, color: string) => void;
    onRemoveDataProductLifecycle: (id: string) => void;
};

export type EditableColumn = DataProductLifeCycleContract & {
    editable: boolean;
};

interface EditableColumnType<T> extends ColumnType<T> {
    editable?: boolean;
}
export const getDataProductTableColumns = ({
    t,
    isDisabled,
    isLoading,
    editColor,
    onRemoveDataProductLifecycle,
}: Props): EditableColumnType<DataProductLifeCycleContract>[] => {
    const sorter = new Sorter<DataProductLifeCycleContract>();
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
            title: t('Value'),
            dataIndex: 'value',
            ellipsis: {
                showTitle: false,
            },
            render: (type: string) => <TableCellItem text={type} />,
            sorter: sorter.stringSorter((dp) => dp.value),
            defaultSortOrder: 'ascend',
            editable: true,
        },
        {
            title: t('Color'),
            dataIndex: 'color',
            ellipsis: {
                showTitle: false,
            },
            render: (color: string, record) => (
                <ColorPicker value={color} onChangeComplete={(color) => editColor(record, color.toHexString())} />
            ),
            sorter: sorter.stringSorter((dp) => dp.color),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Is Default'),
            dataIndex: 'is_default',
            ellipsis: {
                showTitle: false,
            },
            render: (is_default: boolean) => <Checkbox checked={is_default} />,
            sorter: sorter.stringSorter((dp) => dp.is_default.toString()),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (_, { id, is_default }) => {
                return (
                    <Flex vertical>
                        {!is_default && (
                            <Popconfirm
                                title={t('Remove')}
                                description={t(
                                    'Are you sure you want to delete the data product lifecycle? This will remove the lifecycle from all the data products and return them to default',
                                )}
                                onConfirm={() => onRemoveDataProductLifecycle(id)}
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
                        )}
                    </Flex>
                );
            },
        },
    ];
};
