import { Button, Flex, Popconfirm, type TableColumnsType, Tooltip } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { EnvironmentGetItem, GetDomainsItem } from '@/store/api/services/generated/configurationDomainsApi.ts';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    handleRemove: (domain: GetDomainsItem) => void;
    handleEdit: (domain: GetDomainsItem) => () => void;
    availableEnvironments: EnvironmentGetItem[];
};

export const getDomainTableColumns = ({
    t,
    handleRemove,
    handleEdit,
    availableEnvironments,
}: Props): TableColumnsType<GetDomainsItem> => {
    const sorter = new Sorter<GetDomainsItem>();
    const globalEnvironments = availableEnvironments.filter((environment) => environment.is_global !== false);
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
            title: t('Environments'),
            dataIndex: 'environments',
            render: (environments: GetDomainsItem['environments']) => {
                const effectiveEnvironments = environments.length ? environments : globalEnvironments;
                const names = effectiveEnvironments.map((environment) => environment.name);
                const visibleText = names.length > 2 ? `${names.slice(0, 2).join(', ')}, ...` : names.join(', ');
                return (
                    <Tooltip title={names.join(', ')}>
                        <span>{visibleText}</span>
                    </Tooltip>
                );
            },
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (record) => {
                return (
                    <Flex>
                        <Button type="link" onClick={handleEdit(record)}>
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
                            <Button type="link">{t('Remove')}</Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
