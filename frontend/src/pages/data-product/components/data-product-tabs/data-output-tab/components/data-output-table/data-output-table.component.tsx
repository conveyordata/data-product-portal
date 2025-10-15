import { Button, Flex, Form, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DataOutputCard } from '@/components/data-outputs/data-output-card/data-output-card.component.tsx';
import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputsGetContract } from '@/types/data-output';
import type { SearchForm } from '@/types/shared';
import { AddDataOutputPopup } from '../add-data-output-popup/add-data-output-popup.tsx';
import styles from './data-output-table.module.scss';

type Props = {
    dataProductId: string;
    dataOutputs: DataOutputsGetContract;
    onDragStart?: (dataOutputId: string) => void;
    onDragEnd?: () => void;
};

export function DataOutputTable({ dataProductId, dataOutputs, onDragStart, onDragEnd }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [isDragging, setIsDragging] = useState(false);
    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_DATA_OUTPUT,
        },
        { skip: !dataProductId },
    );
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataOutputs = useMemo(() => {
        if (!searchTerm) return dataOutputs;
        return dataOutputs.filter(
            (dataOutput) =>
                dataOutput?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataOutput?.namespace?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataOutput?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        );
    }, [dataOutputs, searchTerm]);

    if (!dataProduct) return null;

    const canCreateDataOutput = access?.allowed || false;

    const handleDragStart = (dataOutputId: string) => {
        setIsDragging(true);
        onDragStart?.(dataOutputId);
    };

    const handleDragEnd = () => {
        setIsDragging(false);
        onDragEnd?.();
    };

    return (
        <Flex vertical className={`${styles.container} ${isDragging ? styles.dragging : ''}`}>
            <Flex justify="space-between" align="center" className={styles.header}>
                <Typography.Title level={4}>{t('Data Outputs')}</Typography.Title>
                <Button
                    disabled={!canCreateDataOutput}
                    type="primary"
                    loading={isLoadingDataProduct}
                    onClick={handleOpen}
                >
                    {t('Add Data Output')}
                </Button>
            </Flex>

            <Searchbar
                placeholder={t('Search data outputs by name or namespace')}
                formItemProps={{ initialValue: '', className: styles.searchBar }}
                form={searchForm}
            />

            <div className={styles.cardsGrid}>
                {filteredDataOutputs.map((dataOutput) => (
                    <DataOutputCard
                        key={dataOutput.id}
                        dataOutput={dataOutput}
                        dataProductId={dataProductId}
                        onDragStart={() => handleDragStart(dataOutput.id)}
                        onDragEnd={handleDragEnd}
                    />
                ))}

                {filteredDataOutputs.length === 0 && (
                    <div className={styles.emptyState}>
                        <Typography.Text type="secondary">
                            {searchTerm ? t('No data outputs found matching your search') : t('No data outputs found')}
                        </Typography.Text>
                    </div>
                )}
            </div>

            {isVisible && <AddDataOutputPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
