import { Flex, TableProps } from 'antd';
import styles from './business-area-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useGetAllBusinessAreasQuery,
    useRemoveBusinessAreaMutation,
    useUpdateBusinessAreaMutation,
} from '@/store/features/business-areas/business-areas-api-slice';
import { BusinessAreaContract } from '@/types/business-area';
import { getBusinessAreaTableColumns } from './business-area-table-columns';
import { EditableTable } from '@/components/editable-table/editable-table.component';
import { useTablePagination } from '@/hooks/use-table-pagination';

export function BussinesAreaTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllBusinessAreasQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const [editBusinessArea, { isLoading: isEditing }] = useUpdateBusinessAreaMutation();
    const [onRemoveBusinessArea, { isLoading: isRemoving }] = useRemoveBusinessAreaMutation();

    const columns = getBusinessAreaTableColumns({ t, onRemoveBusinessArea });

    const onChange: TableProps<BusinessAreaContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleSave = async (row: BusinessAreaContract) => {
        try {
            await editBusinessArea({ businessArea: row, businessAreaId: row.id });
            dispatchMessage({ content: t('Business Area updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update Business Area'), type: 'error' });
        }
    };

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex vertical className={styles.tableFilters}>
                <EditableTable<BusinessAreaContract>
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
