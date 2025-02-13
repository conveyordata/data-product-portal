import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { EditableColumn } from '@/components/editable-table/editable-table.component';
import { DataProductIcon, DataProductTypeContract } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import { Button, Flex, Popconfirm } from 'antd';

type Props = {
    t: TFunction;
    onRemoveDataProductType: (id: string) => void;
};

export const getDataProductTypeTableColumns = ({
    t,
    onRemoveDataProductType,
}: Props): EditableColumn<DataProductTypeContract>[] => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            editable: true,
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
            editable: true,
        },
        {
            title: t('Icon'),
            dataIndex: 'icon_key',
            render: (icon_key: DataProductIcon) => {
                const icon = getDataProductTypeIcon(icon_key);
                return <TableCellItem reactSVGComponent={icon} />;
            },
            editable: true,
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
                            description={t('Are you sure you want to delete the data product type?')}
                            onConfirm={() => onRemoveDataProductType(id)}
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
