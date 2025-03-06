import { Button, Flex, Popconfirm, TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { DomainsGetContract } from '@/types/domain';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    handleRemove: (domain: DomainsGetContract) => void;
    handleEdit: (domain: DomainsGetContract) => () => void;
};

export const getDomainTableColumns = ({ t, handleRemove, handleEdit }: Props): TableColumnsType<DomainsGetContract> => {
    const sorter = new Sorter<DomainsGetContract>();
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
            sorter: sorter.stringSorter((domain) => domain.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
            sorter: sorter.stringSorter((domain) => domain.description),
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
                            description={t('Are you sure you want to delete the Domain?')}
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
