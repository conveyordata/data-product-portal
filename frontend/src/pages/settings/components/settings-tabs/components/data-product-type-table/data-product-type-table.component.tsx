import { Button, Flex, Space, Table, type TableProps, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal';
import { useTablePagination } from '@/hooks/use-table-pagination';
import {
    useGetAllDataProductTypesQuery,
    useRemoveDataProductTypeMutation,
} from '@/store/features/data-product-types/data-product-types-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { DataProductTypesGetContract } from '@/types/data-product-type';

import { CreateDataProductTypeModal } from './data-product-type-form-modal.component';
import { CreateDataProductTypeMigrateModal } from './data-product-type-migrate-modal.component';
import styles from './data-product-type-table.module.scss';
import { getDataProductTypeTableColumns } from './data-product-type-table-columns';

export function DataProductTypeTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllDataProductTypesQuery();
    const { pagination, handlePaginationChange } = useTablePagination(data);
    const { isVisible, handleOpen, handleClose } = useModal();
    const {
        isVisible: migrateModalVisible,
        handleOpen: handleOpenMigrate,
        handleClose: handleCloseMigrate,
    } = useModal();
    const [onRemoveDataProductType] = useRemoveDataProductTypeMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductTypesGetContract | undefined>(undefined);
    const [migrateFrom, setMigrateFrom] = useState<DataProductTypesGetContract | undefined>(undefined);

    const onChange: TableProps<DataProductTypesGetContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: DataProductTypesGetContract) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const handleRemove = async (type: DataProductTypesGetContract) => {
        try {
            if (type.data_product_count > 0) {
                setMigrateFrom(type);
                handleOpenMigrate();
            } else {
                await onRemoveDataProductType(type.id);
                dispatchMessage({ content: t('Type removed successfully'), type: 'success' });
            }
        } catch (_error) {
            dispatchMessage({ content: t('Could not remove Data Product Type'), type: 'error' });
        }
    };

    const columns = getDataProductTypeTableColumns({ t, handleRemove, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.addContainer}>
                <Typography.Title level={3}>{t('Types')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Type')}
                    </Button>
                </Space>
            </Flex>
            <Table<DataProductTypesGetContract>
                dataSource={data}
                columns={columns}
                onChange={onChange}
                pagination={pagination}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                rowClassName={() => 'editable-row'}
                size={'small'}
            />
            {isVisible && initial && (
                <CreateDataProductTypeModal onClose={handleClose} isOpen={isVisible} mode={mode} initial={initial} />
            )}
            {migrateModalVisible && migrateFrom && (
                <CreateDataProductTypeMigrateModal
                    isOpen={migrateModalVisible}
                    onClose={handleCloseMigrate}
                    migrateFrom={migrateFrom}
                />
            )}
        </Flex>
    );
}
