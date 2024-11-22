import { Flex, Table, TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './schema-table.module.scss';
import { useGetDataContractByIdQuery } from '@/store/features/data-contracts/data-contracts-api-slice';
import { ColumnContract } from '@/types/data-contract/column.contract.ts';
import { getSchemaColumns } from './schema-table-columns.tsx';

type Props = {
    dataContractId: string;
}

export function SchemaTable({ dataContractId }: Props) {
    const { t } = useTranslation();
    const { data: dataContract, isLoading } = useGetDataContractByIdQuery(dataContractId);

    const columns: TableColumnsType<ColumnContract> = useMemo(() => {
        return getSchemaColumns({ t });
    }, [t]);

    if (!dataContract?.columns) return null;

    return (
        <>
            <Flex className={styles.schemaListContainer}>
                <Table<ColumnContract>
                    loading={isLoading}
                    className={styles.schemaListTable}
                    columns={columns}
                    dataSource={dataContract.columns}
                    rowKey={({ id }) => id}
                    pagination={false}
                    rowClassName={styles.tableRow}
                    size={'small'}
                />
            </Flex>
        </>
    );
}
