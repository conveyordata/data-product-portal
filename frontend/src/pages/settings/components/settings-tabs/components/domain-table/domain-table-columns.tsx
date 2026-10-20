import { Button, Flex, Popconfirm, type TableColumnsType, Tag } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { DomainStatus, type GetDomainsItem } from '@/store/api/services/generated/configurationDomainsApi.ts';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    handleRemove: (domain: GetDomainsItem) => void;
    handleEdit: (domain: GetDomainsItem) => () => void;
};

export const getDomainTableColumns = ({ t, handleRemove, handleEdit }: Props): TableColumnsType<GetDomainsItem> => {
    const sorter = new Sorter<GetDomainsItem>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (name: string, domain) => (
                <Flex gap="small" align="center">
                    <TableCellItem text={name} tooltip={{ content: name }} />
                    {domain.status === DomainStatus.Deleting && <Tag color="error">{t('Deleting')}</Tag>}
                </Flex>
            ),
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
            render: (record: GetDomainsItem) => {
                const isDeleting = record.status === DomainStatus.Deleting;
                return (
                    <Flex>
                        <Button type="link" onClick={handleEdit(record)} disabled={isDeleting}>
                            {t('Edit')}
                        </Button>
                        <Popconfirm
                            title={t('Remove')}
                            description={t('Are you sure you want to delete the Domain?')}
                            onConfirm={() => handleRemove(record)}
                            placement="leftTop"
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            autoAdjustOverflow={true}
                        >
                            <Button type="link" disabled={isDeleting}>
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
