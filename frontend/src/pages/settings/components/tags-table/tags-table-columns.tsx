import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { TagContract } from '@/types/tag';
import { EditableColumn } from '@/components/editable-table/editable-table.component';
import { Button, Flex, Popconfirm } from 'antd';

type Props = {
    t: TFunction;
    onRemoveTag: (id: string) => void;
    handleEdit: (tag: TagContract) => () => void;
};

export const getTagsTableColums = ({ t, onRemoveTag, handleEdit }: Props): EditableColumn<TagContract>[] => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Value'),
            dataIndex: 'value',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            editable: true,
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (record, { id }) => {
                return (
                    <Flex>
                        <Button type={'link'} onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        <Popconfirm
                            title={t('Remove')}
                            description={t('Are you sure you want to delete the tag?')}
                            onConfirm={() => onRemoveTag(id)}
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
