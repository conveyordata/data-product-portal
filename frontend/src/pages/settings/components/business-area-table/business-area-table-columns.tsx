import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreaContract } from '@/types/business-area';
import { EditableColumn } from '@/components/editable-table/editable-table.component';
import { Button, Flex, Popconfirm } from 'antd';

type Props = {
    t: TFunction;
    onRemoveBusinessArea: (id: string) => void;
};

export const getBusinessAreaTableColumns = ({
    t,
    onRemoveBusinessArea,
}: Props): EditableColumn<BusinessAreaContract>[] => {
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
                            onConfirm={() => onRemoveBusinessArea(id)}
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
