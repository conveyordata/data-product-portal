import { Button, Flex, Space, TableProps, Typography } from 'antd';
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
import { useModal } from '@/hooks/use-modal';
import { useState } from 'react';
import { CreateBusinessAreaModal } from './business-area-form-modal.component';

export function BussinesAreaTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllBusinessAreasQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const [editBusinessArea, { isLoading: isEditing }] = useUpdateBusinessAreaMutation();
    const [onRemoveBusinessArea, { isLoading: isRemoving }] = useRemoveBusinessAreaMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<BusinessAreaContract | undefined>(undefined);

    const onChange: TableProps<BusinessAreaContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: BusinessAreaContract) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const handleSave = async (row: BusinessAreaContract) => {
        try {
            await editBusinessArea({ businessArea: row, businessAreaId: row.id });
            dispatchMessage({ content: t('Business Area updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update Business Area'), type: 'error' });
        }
    };

    const columns = getBusinessAreaTableColumns({ t, onRemoveBusinessArea, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Business Areas')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Business Area')}
                    </Button>
                </Space>
            </Flex>
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
            {isVisible && (
                <CreateBusinessAreaModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
