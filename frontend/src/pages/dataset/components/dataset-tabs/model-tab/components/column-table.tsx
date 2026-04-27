import { Table, Tag } from 'antd';
import type { ColumnType } from 'antd/es/table';
import { useTranslation } from 'react-i18next';
import type { ColumnResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

type Props = {
    columns: ColumnResponse[];
};

export function ColumnTable({ columns }: Props) {
    const { t } = useTranslation();

    const tableColumns: ColumnType<ColumnResponse>[] = [
        {
            title: t('Name'),
            dataIndex: 'name',
            key: 'name',
            render: (name: string) => <code>{name}</code>,
        },
        {
            title: t('Type'),
            dataIndex: 'data_type',
            key: 'data_type',
            render: (type: string | null | undefined) => (type ? <code>{type}</code> : '—'),
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            key: 'description',
            render: (desc: string | null | undefined) => desc ?? '—',
        },
        {
            title: t('Tags'),
            dataIndex: 'tags',
            key: 'tags',
            render: (tags: { id: string; value: string }[]) => tags.map((tag) => <Tag key={tag.id}>{tag.value}</Tag>),
        },
    ];

    return (
        <Table<ColumnResponse>
            dataSource={columns}
            columns={tableColumns}
            rowKey="id"
            pagination={false}
            size="small"
        />
    );
}
