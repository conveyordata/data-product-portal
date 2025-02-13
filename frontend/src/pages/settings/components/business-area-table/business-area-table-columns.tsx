import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreaContract } from '@/types/business-area';
import { EditableColumn } from '@/components/editable-table/editable-table.component';

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
    ];
};
