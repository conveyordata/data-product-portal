import { Button, Checkbox, ColorPicker, Flex, Popconfirm, TableColumnsType } from 'antd';
import { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleEdit: (record: DataProductLifeCycleContract) => () => void;
    handleRemove: (record: DataProductLifeCycleContract) => void;
};

export const getDataProductTableColumns = ({
    t,
    isDisabled,
    isLoading,
    handleEdit,
    handleRemove,
}: Props): TableColumnsType<DataProductLifeCycleContract> => {
    const sorter = new Sorter<DataProductLifeCycleContract>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
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
        },
        {
            title: t('Value'),
            dataIndex: 'value',
            ellipsis: {
                showTitle: false,
            },
            render: (value: number) => <TableCellItem text={value.toString()} />,
            sorter: sorter.numberSorter((dp) => dp.value),
        },
        {
            title: t('Color'),
            dataIndex: 'color',
            ellipsis: {
                showTitle: false,
            },
            render: (color: string) => <ColorPicker value={color} disabled />,
        },
        {
            title: t('Is Default'),
            dataIndex: 'is_default',
            ellipsis: {
                showTitle: false,
            },
            render: (is_default: boolean) => <Checkbox checked={is_default} />,
            sorter: sorter.stringSorter((dp) => dp.is_default.toString()),
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (_, record) => {
                return (
                    <Flex>
                        <Button type={'link'} onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        {!record.is_default && (
                            <Popconfirm
                                title={t('Remove')}
                                description={t(
                                    'Are you sure you want to delete the lifecycle? This will remove the lifecycle from all the data products and datasets and return them to default',
                                )}
                                onConfirm={() => handleRemove(record)}
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
