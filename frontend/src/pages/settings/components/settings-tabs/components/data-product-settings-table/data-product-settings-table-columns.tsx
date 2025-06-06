import { Button, Checkbox, Flex, Input, Popconfirm, Select, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { DataProductSettingContract } from '@/types/data-product-setting';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleEdit: (record: DataProductSettingContract) => () => void;
    handleRemove: (record: DataProductSettingContract) => void;
};

const defaultItem = (setting: DataProductSettingContract) => {
    switch (setting.type) {
        case 'checkbox': {
            const checked = setting.default === 'true';
            return <Checkbox disabled checked={checked} />;
        }
        case 'tags': {
            const list = setting.default.split(',').filter((tag) => tag.length > 0);
            return <Select disabled value={list} allowClear={false} defaultActiveFirstOption mode="tags" />;
        }
        case 'input': {
            const input = setting.default;
            return <Input disabled value={input} />;
        }
        default: {
            const input = setting.default;
            return <Input disabled value={input} />;
        }
    }
};

const typeConversion = (type: string, t: TFunction) => {
    switch (type) {
        case 'checkbox':
            return t('Checkbox');
        case 'tags':
            return t('List');
        case 'input':
            return t('Input');
        default:
            return t('Undefined');
    }
};

export const getDataProductSettingsTableColumns = ({
    t,
    isDisabled,
    isLoading,
    handleEdit,
    handleRemove,
}: Props): TableColumnsType<DataProductSettingContract> => {
    const sorter = new Sorter<DataProductSettingContract>();
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
            sorter: sorter.stringSorter((setting) => setting.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Namespace'),
            dataIndex: 'namespace',
            ellipsis: {
                showTitle: false,
            },
            render: (namespace: string) => <TableCellItem text={namespace} />,
            sorter: sorter.stringSorter((setting) => setting.namespace),
        },
        {
            title: t('Type'),
            dataIndex: 'type',
            ellipsis: {
                showTitle: false,
            },
            render: (type: string) => <TableCellItem text={typeConversion(type, t)} />,
            sorter: sorter.stringSorter((setting) => typeConversion(setting.type, t)),
        },
        {
            title: t('Tooltip'),
            dataIndex: 'tooltip',
            ellipsis: {
                showTitle: false,
            },
            render: (tooltip: string) => <TableCellItem text={tooltip} tooltip={{ content: tooltip }} />,
            sorter: sorter.stringSorter((setting) => setting.tooltip),
        },
        {
            title: t('Category'),
            dataIndex: 'category',
            ellipsis: {
                showTitle: false,
            },
            render: (category: string) => <TableCellItem text={category} />,
            sorter: sorter.stringSorter((setting) => setting.category),
        },
        {
            title: t('Default'),
            dataIndex: 'default',
            ellipsis: {
                showTitle: false,
            },
            render: (_, record) => defaultItem(record),
        },
        {
            title: t('Order'),
            dataIndex: 'order',
            ellipsis: {
                showTitle: false,
            },
            render: (order: number) => <TableCellItem text={order.toString()} />,
            sorter: sorter.numberSorter((setting) => setting.order),
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '15%',
            render: (record) => {
                return (
                    <Flex>
                        <Button type={'link'} onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        <Popconfirm
                            title={t('Remove')}
                            description={t(
                                'Are you sure you want to delete the data product setting? This will remove the setting from all the data products',
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
                    </Flex>
                );
            },
        },
    ];
};
