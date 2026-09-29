import { InfoCircleOutlined } from '@ant-design/icons';
import { Button, Flex, Popconfirm, type TableColumnsType, Tooltip } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { OutputPortAccessTypesGetItem } from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import { compareAccessFunctions, getAccessFunctionInfo } from '@/utils/access-function.helper.tsx';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    handleEdit: (record: OutputPortAccessTypesGetItem) => () => void;
    handleRemove: (record: OutputPortAccessTypesGetItem) => void;
    lastInviteOnlyId?: string;
};

const titleWithInfo = (title: string, info: string, justify?: 'flex-end') => (
    <Flex align="center" gap="small" justify={justify}>
        {title}
        <Tooltip title={info}>
            <InfoCircleOutlined style={{ color: 'var(--ant-color-text-secondary)', cursor: 'help' }} />
        </Tooltip>
    </Flex>
);

export const getOutputPortAccessTypesTableColumns = ({
    t,
    handleEdit,
    handleRemove,
    lastInviteOnlyId,
}: Props): TableColumnsType<OutputPortAccessTypesGetItem> => {
    const sorter = new Sorter<OutputPortAccessTypesGetItem>();
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
            title: titleWithInfo(
                t('Function'),
                t(
                    'Decides how access requests are handled: approved automatically, approved by the owner, or invite only with the Output Port hidden.',
                ),
            ),
            dataIndex: 'access_function',
            width: '15%',
            render: (_, record) => {
                const { label, tooltip } = getAccessFunctionInfo(t, record.access_function);
                return (
                    <Tooltip title={tooltip ?? t('Access requests are approved automatically')}>
                        <span>{label}</span>
                    </Tooltip>
                );
            },
            sorter: (a, b) => compareAccessFunctions(a.access_function, b.access_function),
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            ellipsis: { showTitle: false },
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
        },
        {
            title: titleWithInfo(
                t('Output Ports'),
                t("Number of Output Ports using this access type. An access type that is in use can't be removed."),
                'flex-end',
            ),
            dataIndex: 'output_port_count',
            width: '10%',
            align: 'right',
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '15%',
            render: (_, record) => {
                const removeBlockedReason =
                    record.id === lastInviteOnlyId
                        ? t('At least one access type must stay Invite only')
                        : record.output_port_count > 0
                          ? t('Reassign the {{count}} Output Ports using this access type first', {
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
                                description={t('Are you sure you want to delete the access type?')}
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
