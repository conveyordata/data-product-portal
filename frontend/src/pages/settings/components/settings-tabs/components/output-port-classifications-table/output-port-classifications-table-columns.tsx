import { Button, Flex, Popconfirm, type TableColumnsType, Tooltip } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { OutputPortClassificationsGetItem } from '@/store/api/services/generated/configurationOutputPortClassificationsApi.ts';
import { compareAccessFunctions, getAccessFunctionLabel } from '@/utils/access-type.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    handleEdit: (record: OutputPortClassificationsGetItem) => () => void;
    handleRemove: (record: OutputPortClassificationsGetItem) => void;
    lastInviteOnlyId?: string;
};

export const getOutputPortClassificationsTableColumns = ({
    t,
    handleEdit,
    handleRemove,
    lastInviteOnlyId,
}: Props): TableColumnsType<OutputPortClassificationsGetItem> => {
    const sorter = new Sorter<OutputPortClassificationsGetItem>();
    return [
        {
            title: t('Name'),
            dataIndex: 'name',
            width: '15%',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            sorter: sorter.stringSorter((c) => c.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            ellipsis: { showTitle: false },
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
        },
        {
            title: t('Access function'),
            dataIndex: 'access_type',
            width: '15%',
            render: (_, record) => <TableCellItem text={getAccessFunctionLabel(t, record.access_type)} />,
            sorter: (a, b) => compareAccessFunctions(a.access_type, b.access_type),
        },
        {
            title: t('Output Ports'),
            dataIndex: 'output_port_count',
            width: '10%',
            onCell: () => ({ style: { textAlign: 'right' } }),
            sorter: sorter.numberSorter((c) => c.output_port_count),
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '15%',
            render: (_, record) => {
                const removeBlockedReason =
                    record.id === lastInviteOnlyId
                        ? t('At least one classification must stay Invite only')
                        : record.output_port_count > 0
                          ? t('Reassign the {{count}} Output Ports using this classification first', {
                                count: record.output_port_count,
                            })
                          : undefined;
                return (
                    <Flex>
                        <Button type="link" onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        {removeBlockedReason ? (
                            <Tooltip title={removeBlockedReason}>
                                <Button type="link" disabled>
                                    {t('Remove')}
                                </Button>
                            </Tooltip>
                        ) : (
                            <Popconfirm
                                title={t('Remove')}
                                description={t('Are you sure you want to delete the classification?')}
                                onConfirm={() => handleRemove(record)}
                                placement="leftTop"
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                            >
                                <Button type="link">{t('Remove')}</Button>
                            </Popconfirm>
                        )}
                    </Flex>
                );
            },
        },
    ];
};
