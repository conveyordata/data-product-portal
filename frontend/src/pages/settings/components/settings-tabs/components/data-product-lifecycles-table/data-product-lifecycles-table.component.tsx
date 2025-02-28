import type { TableProps } from 'antd';
import { Button, Flex, Space, Table, Typography } from 'antd';
import styles from './data-product-lifecycles-table.module.scss';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getDataProductTableColumns } from './data-product-lifecycles-table-columns.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    useGetAllDataProductLifecyclesQuery,
    useRemoveDataProductLifecycleMutation,
} from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { useModal } from '@/hooks/use-modal.tsx';
import { CreateLifecycleModal } from './new-data-product-lifecycles-modal.component.tsx';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

export function DataProductLifecyclesTable() {
    const { t } = useTranslation();
    const { data: dataProductLifecycles = [], isFetching } = useGetAllDataProductLifecyclesQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductLifeCycleContract | undefined>(undefined);
    const [onRemoveDataProductLifecycle, { isLoading: isRemoving }] = useRemoveDataProductLifecycleMutation();

    const onChange: TableProps<DataProductLifeCycleContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (lifeCycle: DataProductLifeCycleContract) => () => {
        setMode('edit');
        setInitial(lifeCycle);
        handleOpen();
    };

    const handleRemove = async (lifeCycle: DataProductLifeCycleContract) => {
        try {
            await onRemoveDataProductLifecycle(lifeCycle.id);
            dispatchMessage({ content: t('Lifecycle removed successfully'), type: 'success' });
        } catch (_) {
            dispatchMessage({ content: t('Could not remove lifecycle'), type: 'error' });
        }
    };

    const columns = useMemo(
        () => getDataProductTableColumns({ t, handleEdit, handleRemove }),
        [t, dataProductLifecycles],
    );

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Lifecycles')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Lifecycle')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<DataProductLifeCycleContract>
                    dataSource={dataProductLifecycles}
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
                <CreateLifecycleModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
