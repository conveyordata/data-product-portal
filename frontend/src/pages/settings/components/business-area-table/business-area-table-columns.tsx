import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreasGetContract } from '@/types/business-area';
import { EditableColumn } from '@/components/editable-table/editable-table.component';
import { Button, Flex, Popconfirm } from 'antd';

type Props = {
    t: TFunction;
    handleRemove: (businessArea: BusinessAreasGetContract) => void;
    handleEdit: (businessArea: BusinessAreasGetContract) => () => void;
};

export const getBusinessAreaTableColumns = ({
    t,
    handleRemove,
    handleEdit,
}: Props): EditableColumn<BusinessAreasGetContract>[] => {
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
            render: (record) => {
                return (
                    <Flex>
                        <Button type={'link'} onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        <Popconfirm
                            title={t('Remove')}
                            description={t('Are you sure you want to delete the Business Area?')}
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
