import { Button, Flex, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import {
    type DataProductSettingScope,
    type DataProductSettingsGetItem,
    useGetDataProductsSettingsQuery,
    useRemoveDataProductSettingMutation,
} from '@/store/api/services/generated/configurationDataProductSettingsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import styles from './data-product-settings-table.module.scss';
import { getDataProductSettingsTableColumns } from './data-product-settings-table-columns.tsx';
import { CreateSettingModal } from './new-data-product-setting-modal.component.tsx';

type Props = {
    scope: DataProductSettingScope;
};

export function DataProductSettingsTable({ scope }: Props) {
    const { t } = useTranslation();
    const { data: dataProductSettings = undefined, isFetching } = useGetDataProductsSettingsQuery();

    const filteredSettings = useMemo(() => {
        return dataProductSettings?.data_product_settings.filter((setting) => setting.scope === scope) ?? [];
    }, [dataProductSettings, scope]);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductSettingsGetItem | undefined>(undefined);
    const [onRemoveDataProductSetting] = useRemoveDataProductSettingMutation();

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = useCallback(
        (setting: DataProductSettingsGetItem) => () => {
            setMode('edit');
            setInitial(setting);
            handleOpen();
        },
        [handleOpen],
    );

    const handleRemove = useCallback(
        async (setting: DataProductSettingsGetItem) => {
            try {
                await onRemoveDataProductSetting(setting.id);
                dispatchMessage({ content: t('Data Product lifecycle removed successfully'), type: 'success' });
            } catch (_) {
                dispatchMessage({ content: t('Could not remove Data Product lifecycle'), type: 'error' });
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
        <Flex vertical gap={'large'}>
            <Flex justify={'space-between'} align={'center'}>
                <Typography.Title level={3}>{t('Custom Settings')}</Typography.Title>
                <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                    {t('Add custom setting')}
                </Button>
            </Flex>
            <Table<DataProductSettingsGetItem>
                dataSource={filteredSettings}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                size={'small'}
            />
            {isVisible && (mode === 'create' || initial) && (
                <CreateSettingModal scope={scope} onClose={onClose} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
