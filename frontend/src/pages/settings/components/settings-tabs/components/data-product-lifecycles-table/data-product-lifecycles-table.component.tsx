import { Button, Flex, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import {
    type DataProductLifeCyclesGetItem,
    useGetDataProductsLifecyclesQuery,
    useRemoveDataProductLifecycleMutation,
} from '@/store/api/services/generated/configurationDataProductLifecyclesApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import styles from './data-product-lifecycles-table.module.scss';
import { getDataProductTableColumns } from './data-product-lifecycles-table-columns.tsx';
import { CreateLifecycleModal } from './new-data-product-lifecycles-modal.component.tsx';

export function DataProductLifecyclesTable() {
    const { t } = useTranslation();
    const { data: dataProductLifecycles = undefined, isFetching } = useGetDataProductsLifecyclesQuery();
    const { isVisible, handleOpen, handleClose } = useModal();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductLifeCyclesGetItem | undefined>(undefined);
    const [onRemoveDataProductLifecycle] = useRemoveDataProductLifecycleMutation();

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = useCallback(
        (lifeCycle: DataProductLifeCyclesGetItem) => () => {
            setMode('edit');
            setInitial(lifeCycle);
            handleOpen();
        },
        [handleOpen],
    );

    const handleRemove = useCallback(
        async (lifeCycle: DataProductLifeCyclesGetItem) => {
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
        <Flex vertical gap={'large'}>
            <Flex justify={'space-between'} align={'center'}>
                <Typography.Title level={3}>{t('Lifecycles')}</Typography.Title>
                <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                    {t('Add Lifecycle')}
                </Button>
            </Flex>
            <Table<DataProductLifeCyclesGetItem>
                dataSource={dataProductLifecycles?.data_product_life_cycles}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                size={'small'}
            />
            {isVisible && (mode === 'create' || initial) && (
                <CreateLifecycleModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
