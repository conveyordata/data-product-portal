import { Button, Flex, Space, Table, TableProps, Typography } from 'antd';
import styles from './domain-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useGetAllDomainsQuery, useRemoveDomainMutation } from '@/store/features/domains/domains-api-slice';
import { DomainsGetContract } from '@/types/domain';
import { getDomainTableColumns } from './domain-table-columns';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useModal } from '@/hooks/use-modal';
import { useState } from 'react';
import { CreateDomainModal } from './domain-form-modal.component';
import { CreateDomainMigrateModal } from './domain-migrate-modal.component';

export function DomainTable() {
    const { t } = useTranslation();
    const { data = [], isFetching } = useGetAllDomainsQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const {
        isVisible: migrateModalVisible,
        handleOpen: handleOpenMigrate,
        handleClose: handleCloseMigrate,
    } = useModal();
    const [onRemoveDomain, { isLoading: isRemoving }] = useRemoveDomainMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DomainsGetContract | undefined>(undefined);
    const [migrateFrom, setMigrateFrom] = useState<DomainsGetContract | undefined>(undefined);

    const onChange: TableProps<DomainsGetContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: DomainsGetContract) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const handleRemove = async (domain: DomainsGetContract) => {
        try {
            if (domain.dataset_count > 0 || domain.data_product_count > 0) {
                setMigrateFrom(domain);
                handleOpenMigrate();
            } else {
                await onRemoveDomain(domain.id);
                dispatchMessage({ content: t('Domain removed successfully'), type: 'success' });
            }
        } catch (error) {
            dispatchMessage({ content: t('Could not remove Domain'), type: 'error' });
        }
    };

    const columns = getDomainTableColumns({ t, handleRemove, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.addContainer}>
                <Typography.Title level={3}>{t('Domains')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Domain')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<DomainsGetContract>
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
                <CreateDomainModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
            {migrateModalVisible && (
                <CreateDomainMigrateModal
                    isOpen={migrateModalVisible}
                    t={t}
                    onClose={handleCloseMigrate}
                    migrateFrom={migrateFrom}
                />
            )}
        </Flex>
    );
}
