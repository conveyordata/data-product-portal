import { TableColumnsType } from 'antd';
import { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { ColumnContract } from '@/types/data-contract';

export const getSchemaColumns = ({ t }: { t: TFunction }): TableColumnsType<ColumnContract> => {
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
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
        },
        {
            title: t('Data type'),
            dataIndex: 'data_type',
            render: (dataType: string) => <TableCellItem text={dataType} tooltip={{ content: dataType }} />,
        },
        {
            title: t('Quality checks'),
            dataIndex: 'checks',
            render: (checks: string[]) => {
                const qualityChecks = checks.join(', ');
                return <TableCellItem text={qualityChecks} tooltip={{ content: qualityChecks }} />;
            },
        },
    ];
};
