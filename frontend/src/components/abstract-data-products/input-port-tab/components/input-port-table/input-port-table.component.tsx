import type { TableColumnsType, TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { EmptyStateFilter, EmptyStateQuery } from '@/components/empty-state/empty-state.component.tsx';
import { OutputPortOutlined } from '@/components/icons';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { DEFAULT_TABLE_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import type { AbstractDataProductInputPort as InputPort } from '@/store/api/services/generated/dataProductsApi.ts';
import styles from './input-port-table.module.scss';
import { getDataProductDatasetsColumns } from './input-port-table-columns.tsx';

type Props = {
    canRemoveAccess: boolean;
    canRequestAccess: boolean;
    handleCancel: (outputPortId: string) => Promise<void>;
    handleRevoke: (outputPortId: string) => Promise<void>;
    handleRenew: (outputPortId: string) => Promise<void>;
    inputPorts: InputPort[];
    query: EmptyStateQuery;
    filter?: EmptyStateFilter;
};
export function InputPortTable({
    canRemoveAccess,
    canRequestAccess,
    handleCancel,
    handleRevoke,
    handleRenew,
    inputPorts,
    query,
    filter,
}: Props) {
    const { t } = useTranslation();

    const { pagination, handlePaginationChange } = useTablePagination(inputPorts, {
        initialPagination: DEFAULT_TABLE_PAGINATION,
    });

    const onChange: TableProps<InputPort>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns: TableColumnsType<InputPort> = useMemo(() => {
        return getDataProductDatasetsColumns({
            t,
            canRemoveAccess: canRemoveAccess,
            canRequestAccess: canRequestAccess,
            handleCancel,
            handleRevoke,
            handleRenew,
            inputPorts: inputPorts,
        });
    }, [t, inputPorts, canRemoveAccess, canRequestAccess, handleCancel, handleRevoke, handleRenew]);

    return (
        <ListTable<InputPort>
            query={query}
            dataSource={inputPorts}
            columns={columns}
            subject={t('Input Ports')}
            emptyState={{
                icon: <OutputPortOutlined />,
                title: t('No Input Ports yet'),
                description: t('Request access to an Output Port in the Marketplace to consume its data here.'),
            }}
            onChange={onChange}
            filter={filter}
            className={styles.datasetListTable}
            rowKey={({ id }) => id}
            pagination={{
                ...pagination,
                placement: ['topEnd'],
                size: 'small',
                showTotal: (total, range) =>
                    t('Showing {{range0}}-{{range1}} of {{count}} Output Ports', {
                        range0: range[0],
                        range1: range[1],
                        count: total,
                    }),
                className: styles.pagination,
            }}
            rowClassName={styles.tableRow}
            size="small"
        />
    );
}
