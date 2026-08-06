import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useTranslation } from 'react-i18next';
import type { AccessMode } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

type Props = {
    accessModes: AccessMode[];
    selectionMode?: 'multiple' | 'single';
    value?: string[];
    loading?: boolean;
    onChange?: (selectedIds: string[]) => void;
};

export function AccessModeSelector({ loading, value, selectionMode, accessModes, onChange }: Props) {
    const { t } = useTranslation();

    const columns: ColumnsType<AccessMode> = [
        {
            title: t('Name'),
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            key: 'description',
        },
    ];

    const isSingleSelection = selectionMode === 'single';
    const selectedRowKeys = isSingleSelection ? (value?.[0] ? [value[0]] : []) : (value ?? []);

    return (
        <Table<AccessMode>
            dataSource={accessModes}
            columns={columns}
            rowKey="id"
            pagination={false}
            size="small"
            loading={loading}
            rowSelection={{
                type: isSingleSelection ? 'radio' : 'checkbox',
                selectedRowKeys,
                onChange: (nextSelectedRowKeys) => {
                    onChange?.((nextSelectedRowKeys as string[]).slice(0, isSingleSelection ? 1 : undefined));
                },
            }}
        />
    );
}
