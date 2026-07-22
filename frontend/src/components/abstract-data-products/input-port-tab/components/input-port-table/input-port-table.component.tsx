import { Table, type TableColumnsType, type TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { DEFAULT_TABLE_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import type { AbstractDataProductInputPort as InputPort } from '@/store/api/services/generated/dataProductsApi.ts';
import styles from './input-port-table.module.scss';
import { getDataProductDatasetsColumns } from './input-port-table-columns.tsx';

type Props = {
    canRemoveAccess: boolean;
    canRequestAccess: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    handleRenew: (outputPortId: string) => Promise<void>;
    inputPorts: InputPort[];
    loadingInputPorts: boolean;
};
export function InputPortTable({
    canRemoveAccess,
    canRequestAccess,
    handleRemove,
    handleRenew,
    inputPorts,
    loadingInputPorts,
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
            handleRemove,
            handleRenew,
            inputPorts: inputPorts,
        });
    }, [t, inputPorts, canRemoveAccess, canRequestAccess, handleRemove, handleRenew]);

    return (
        <Table<InputPort>
            loading={loadingInputPorts}
            className={styles.datasetListTable}
            columns={columns}
            dataSource={inputPorts}
            rowKey={({ id }) => id}
            onChange={onChange}
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
            size={'small'}
        />
    );
}
