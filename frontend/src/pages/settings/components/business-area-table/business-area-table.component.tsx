import { Button, Flex, Space, Table, TableProps, Typography } from 'antd';
import styles from './business-area-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import {
    useGetAllBusinessAreasQuery,
    useRemoveBusinessAreaMutation,
} from '@/store/features/business-areas/business-areas-api-slice';
import { BusinessAreasGetContract } from '@/types/business-area';
import { getBusinessAreaTableColumns } from './business-area-table-columns';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useModal } from '@/hooks/use-modal';
import { useState } from 'react';
import { CreateBusinessAreaModal } from './business-area-form-modal.component';
import { CreateBusinessAreaMigrateModal } from './business-area-migrate-modal.component';

export function BussinesAreaTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllBusinessAreasQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const {
        isVisible: migrateModalVisible,
        handleOpen: handleOpenMigrate,
        handleClose: handleCloseMigrate,
    } = useModal();
    const [onRemoveBusinessArea, { isLoading: isRemoving }] = useRemoveBusinessAreaMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<BusinessAreasGetContract | undefined>(undefined);
    const [migrateFrom, setMigrateFrom] = useState<BusinessAreasGetContract | undefined>(undefined);

    const onChange: TableProps<BusinessAreasGetContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: BusinessAreasGetContract) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const handleRemove = async (businessArea: BusinessAreasGetContract) => {
        try {
            console.log(businessArea);
            if (businessArea.dataset_count > 0 || businessArea.data_product_count > 0) {
                setMigrateFrom(businessArea);
                handleOpenMigrate();
            } else {
                await onRemoveBusinessArea(businessArea.id);
                dispatchMessage({ content: t('Business Area removed successfully'), type: 'success' });
            }
        } catch (error) {
            dispatchMessage({ content: t('Could not remove Business Area'), type: 'error' });
        }
    };

    const columns = getBusinessAreaTableColumns({ t, handleRemove, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.addContainer}>
                <Typography.Title level={3}>{t('Business Areas')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Business Area')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<BusinessAreasGetContract>
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
            </Flex>
            {isVisible && (
                <CreateBusinessAreaModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
            {migrateModalVisible && (
                <CreateBusinessAreaMigrateModal
                    isOpen={migrateModalVisible}
                    t={t}
                    onClose={handleCloseMigrate}
                    migrateFrom={migrateFrom}
                />
            )}
        </Flex>
    );
}
