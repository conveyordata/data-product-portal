import { Flex, TableProps } from 'antd';
import styles from './data-product-type-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllDataProductTypesQuery } from '@/store/features/data-product-types/data-product-types-api-slice';
import { DataProductTypeContract } from '@/types/data-product-type';
import { getDataProductTypeTableColumns } from './data-product-type-table-columns';
import { EditableTable } from '@/components/editable-table/editable-table.component';
import { useTablePagination } from '@/hooks/use-table-pagination';

export function DataProductTypeTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllDataProductTypesQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const onRemoveDataProductType = () => {};

    const columns = getDataProductTypeTableColumns({ t, onRemoveDataProductType });

    const onChange: TableProps<DataProductTypeContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleSave = async (row: DataProductTypeContract) => {
        try {
            dispatchMessage({ content: t('Data Product Type updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update Data Product Type'), type: 'error' });
        }
    };

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex vertical className={styles.tableFilters}>
                <EditableTable<DataProductTypeContract>
                    data={data}
                    columns={columns}
                    handleSave={handleSave}
                    onChange={onChange}
                    pagination={pagination}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={() => 'editable-row'}
                    size={'small'}
                />
            </Flex>
        </Flex>
    );
}
