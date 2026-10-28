import { AppstoreOutlined } from '@ant-design/icons';
import { Button, Flex, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ListTable } from '@/components/list-table/list-table.component.tsx';

import { useModal } from '@/hooks/use-modal';
import {
    type DataProductTypesGetItem,
    useGetDataProductsTypesQuery,
    useRemoveDataProductTypeMutation,
} from '@/store/api/services/generated/configurationDataProductTypesApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { CreateDataProductTypeModal } from './data-product-type-form-modal.component';
import { CreateDataProductTypeMigrateModal } from './data-product-type-migrate-modal.component';
import styles from './data-product-type-table.module.scss';
import { getDataProductTypeTableColumns } from './data-product-type-table-columns';

export function DataProductTypeTable() {
    const { t } = useTranslation();
    const typesQuery = useGetDataProductsTypesQuery();
    const { data = undefined } = typesQuery;
    const { isVisible, handleOpen, handleClose } = useModal();
    const {
        isVisible: migrateModalVisible,
        handleOpen: handleOpenMigrate,
        handleClose: handleCloseMigrate,
    } = useModal();
    const [onRemoveDataProductType] = useRemoveDataProductTypeMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<DataProductTypesGetItem | undefined>(undefined);
    const [migrateFrom, setMigrateFrom] = useState<DataProductTypesGetItem | undefined>(undefined);

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: DataProductTypesGetItem) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const handleRemove = async (type: DataProductTypesGetItem) => {
        try {
            if (type.data_product_count > 0) {
                setMigrateFrom(type);
                handleOpenMigrate();
            } else {
                await onRemoveDataProductType(type.id).unwrap();
                dispatchMessage({ content: t('Type removed successfully'), type: 'success' });
            }
        } catch (_error) {
            dispatchMessage({ content: t('Could not remove Data Product Type'), type: 'error' });
        }
    };

    const columns = getDataProductTypeTableColumns({ t, handleRemove, handleEdit });

    return (
        <Flex vertical gap="large">
            <Flex justify="space-between" align="center" gap="small">
                <Typography.Title level={3}>{t('Types')}</Typography.Title>
                <Button className={styles.formButton} type="primary" onClick={handleAdd}>
                    {t('Add Type')}
                </Button>
            </Flex>
            <ListTable<DataProductTypesGetItem>
                query={typesQuery}
                dataSource={data?.data_product_types ?? []}
                columns={columns}
                subject={t('Data Product Types')}
                emptyState={{
                    icon: <AppstoreOutlined />,
                    title: t('No Data Product Types yet'),
                    description: t(
                        'Types describe the shape of a Data Product, such as source aligned or consumer aligned.',
                    ),
                }}
                rowKey={(record) => record.id}
                rowHoverable
                size="small"
            />
            {isVisible && (mode === 'create' || initial) && (
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
