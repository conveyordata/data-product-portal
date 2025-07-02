import type { TableProps } from 'antd';
import { Button, Flex, Space, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    useGetAllDataProductLifecyclesQuery,
    useRemoveDataProductLifecycleMutation,
} from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import styles from './data-product-lifecycles-table.module.scss';
import { getDataProductTableColumns } from './data-product-lifecycles-table-columns.tsx';
import { CreateLifecycleModal } from './new-data-product-lifecycles-modal.component.tsx';

export function DataProductLifecyclesTable() {
    const { t } = useTranslation();
    const { data: dataProductLifecycles = [], isFetching } = useGetAllDataProductLifecyclesQuery();
    const { pagination, handlePaginationChange } = useTablePagination(dataProductLifecycles);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductLifeCycleContract | undefined>(undefined);
    const [onRemoveDataProductLifecycle] = useRemoveDataProductLifecycleMutation();

    const onChange: TableProps<DataProductLifeCycleContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = useCallback(
        (lifeCycle: DataProductLifeCycleContract) => () => {
            setMode('edit');
            setInitial(lifeCycle);
            handleOpen();
        },
        [handleOpen],
    );

    const handleRemove = useCallback(
        async (lifeCycle: DataProductLifeCycleContract) => {
            try {
                await onRemoveDataProductLifecycle(lifeCycle.id);
                dispatchMessage({ content: t('Lifecycle removed successfully'), type: 'success' });
            } catch (_) {
                dispatchMessage({ content: t('Could not remove lifecycle'), type: 'error' });
            }
        },
        [t, onRemoveDataProductLifecycle],
    );

    const columns = useMemo(
        () => getDataProductTableColumns({ t, handleEdit, handleRemove }),
        [t, handleEdit, handleRemove],
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
            {isVisible && (mode === 'create' || initial) && (
                <CreateLifecycleModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
