import { Button, Flex, Space, Table, TableProps, Typography } from 'antd';
import styles from './data-product-type-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useGetAllDataProductTypesQuery,
    useRemoveDataProductTypeMutation,
} from '@/store/features/data-product-types/data-product-types-api-slice';
import { DataProductTypesGetContract } from '@/types/data-product-type';
import { getDataProductTypeTableColumns } from './data-product-type-table-columns';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useModal } from '@/hooks/use-modal';
import { useState } from 'react';
import { CreateDataProductTypeModal } from './data-product-type-form-modal.component';
import { CreateDataProductTypeMigrateModal } from './data-product-type-migrate-modal.component';

export function DataProductTypeTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllDataProductTypesQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
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
                dispatchMessage({ content: t('Data Product Type removed successfully'), type: 'success' });
            }
        } catch (_error) {
            dispatchMessage({ content: t('Could not remove Data Product Type'), type: 'error' });
        }
    };

    const columns = getDataProductTypeTableColumns({ t, handleRemove, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.addContainer}>
                <Typography.Title level={3}>{t('Data Product Types')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Data Product Type')}
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
            {isVisible && (
                <CreateDataProductTypeModal
                    onClose={handleClose}
                    t={t}
                    isOpen={isVisible}
                    mode={mode}
                    initial={initial}
                />
            )}
            {migrateModalVisible && (
                <CreateDataProductTypeMigrateModal
                    isOpen={migrateModalVisible}
                    t={t}
                    onClose={handleCloseMigrate}
                    migrateFrom={migrateFrom}
                />
            )}
        </Flex>
    );
}
