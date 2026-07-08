import { Table, type TableColumnsType, type TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import type {
    InputPort,
    RequestInputPortsForDataProductApiArg,
} from '@/store/api/services/generated/dataProductsApi.ts';
import styles from './input-port-table.module.scss';
import { getDataProductDatasetsColumns } from './input-port-table-columns.tsx';

type Props = {
    canRemoveAccess: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    inputPorts: InputPort[];
    loadingInputPorts: boolean;
    handleRenewalRequest: (request: RequestInputPortsForDataProductApiArg) => Promise<void>;
    abstractDataProductId: string;
};
export function InputPortTable({
    canRemoveAccess,
    handleRemove,
    inputPorts,
    loadingInputPorts,
    handleRenewalRequest,
    abstractDataProductId,
}: Props) {
    const { t } = useTranslation();

    const { pagination, handlePaginationChange } = useTablePagination(inputPorts, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<InputPort>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns: TableColumnsType<InputPort> = useMemo(() => {
        return getDataProductDatasetsColumns({
            t,
            canRemoveAccess: canRemoveAccess,
            handleRemove,
            inputPorts: inputPorts,
            handleRenewalRequest,
            abstractDataProductId,
        });
    }, [t, inputPorts, canRemoveAccess, handleRemove, handleRenewalRequest, abstractDataProductId]);

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
