import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { DataProductIcon, DataProductTypesGetContract } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import { Button, Flex, Popconfirm, TableColumnsType } from 'antd';
import { Sorter } from '@/utils/table-sorter.helper';

const iconColumnWidth = 30;

type Props = {
    t: TFunction;
    handleRemove: (type: DataProductTypesGetContract) => void;
    handleEdit: (type: DataProductTypesGetContract) => () => void;
};

export const getDataProductTypeTableColumns = ({
    t,
    handleRemove,
    handleEdit,
}: Props): TableColumnsType<DataProductTypesGetContract> => {
    const sorter = new Sorter<DataProductTypesGetContract>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Icon'),
            dataIndex: 'icon_key',
            width: iconColumnWidth,
            render: (icon_key: DataProductIcon) => {
                const icon = getDataProductTypeIcon(icon_key);
                return <TableCellItem reactSVGComponent={icon} />;
            },
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            sorter: sorter.stringSorter((type) => type.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
            sorter: sorter.stringSorter((type) => type.description),
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (record) => {
                return (
                    <Flex>
                        <Button type={'link'} onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        <Popconfirm
                            title={t('Remove')}
                            description={t('Are you sure you want to delete the Data Product Type?')}
                            onConfirm={() => handleRemove(record)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            autoAdjustOverflow={true}
                        >
                            <Button type={'link'}>{t('Remove')}</Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
