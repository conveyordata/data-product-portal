import type { TableProps } from 'antd';
import { Button, Flex, Space, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    useGetAllDataProductSettingsQuery,
    useRemoveDataProductSettingMutation,
} from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { DataProductSettingContract, DataProductSettingScope } from '@/types/data-product-setting';

import { getDataProductSettingsTableColumns } from './data-product-settings-table-columns.tsx';
import styles from './data-product-settings-table.module.scss';
import { CreateSettingModal } from './new-data-product-setting-modal.component.tsx';

type Props = {
    scope: DataProductSettingScope;
};

export function DataProductSettingsTable({ scope }: Props) {
    const { t } = useTranslation();
    const { data: dataProductSettings = [], isFetching } = useGetAllDataProductSettingsQuery();
    const filteredSettings = useMemo(() => {
        return dataProductSettings.filter((setting) => setting.scope === scope);
    }, [dataProductSettings, scope]);
    const { pagination, handlePaginationChange } = useTablePagination(filteredSettings);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductSettingContract | undefined>(undefined);
    const [onRemoveDataProductSetting] = useRemoveDataProductSettingMutation();

    const onChange: TableProps<DataProductSettingContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = useCallback(
        (setting: DataProductSettingContract) => () => {
            setMode('edit');
            setInitial(setting);
            handleOpen();
        },
        [handleOpen],
    );

    const handleRemove = useCallback(
        async (setting: DataProductSettingContract) => {
            try {
                await onRemoveDataProductSetting(setting.id);
                dispatchMessage({ content: t('Data product lifecycle removed successfully'), type: 'success' });
            } catch (_) {
                dispatchMessage({ content: t('Could not remove data product lifecycle'), type: 'error' });
            }
        },
        [t, onRemoveDataProductSetting],
    );

    const onClose = () => {
        setInitial(undefined);
        handleClose();
    };

    const columns = useMemo(
        () => getDataProductSettingsTableColumns({ t, handleEdit, handleRemove }),
        [t, handleEdit, handleRemove],
    );

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Custom Settings')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Custom Setting')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<DataProductSettingContract>
                    dataSource={filteredSettings}
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
            {isVisible && initial && (
                <CreateSettingModal scope={scope} onClose={onClose} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
