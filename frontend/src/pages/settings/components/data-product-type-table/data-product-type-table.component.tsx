import { Button, Flex, Space, TableProps, Typography } from 'antd';
import styles from './data-product-type-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useGetAllDataProductTypesQuery,
    useRemoveDataProductTypeMutation,
    useUpdateDataProductTypeMutation,
} from '@/store/features/data-product-types/data-product-types-api-slice';
import { DataProductTypeContract } from '@/types/data-product-type';
import { getDataProductTypeTableColumns } from './data-product-type-table-columns';
import { EditableTable } from '@/components/editable-table/editable-table.component';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { CreateBusinessAreaModal } from '../business-area-table/business-area-form-modal.component';
import { useModal } from '@/hooks/use-modal';
import { useState } from 'react';
import { CreateDataProductTypeModal } from './data-product-type-form-modal.component';

export function DataProductTypeTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllDataProductTypesQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const [editDataProductType, { isLoading: isEditing }] = useUpdateDataProductTypeMutation();
    const [onRemoveDataProductType, { isLoading: isRemoving }] = useRemoveDataProductTypeMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductTypeContract | undefined>(undefined);

    const onChange: TableProps<DataProductTypeContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: DataProductTypeContract) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const handleSave = async (row: DataProductTypeContract) => {
        try {
            await editDataProductType({ dataProductType: row, dataProductTypeId: row.id });
            dispatchMessage({ content: t('Data Product Type updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update Data Product Type'), type: 'error' });
        }
    };

    const columns = getDataProductTypeTableColumns({ t, onRemoveDataProductType, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Data Product Types')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Data Product Type')}
                    </Button>
                </Space>
            </Flex>
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
            {isVisible && (
                <CreateDataProductTypeModal
                    onClose={handleClose}
                    t={t}
                    isOpen={isVisible}
                    mode={mode}
                    initial={initial}
                />
            )}
        </Flex>
    );
}
