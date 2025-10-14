import { Button, Flex, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputsGetContract } from '@/types/data-output';

import { AddDataOutputPopup } from '../add-data-output-popup/add-data-output-popup.tsx';
import { DataOutputCard } from './data-output-card.component';
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

            <div className={styles.cardsGrid}>
                {dataOutputs.map((dataOutput) => (
                    <DataOutputCard
                        key={dataOutput.id}
                        dataOutput={dataOutput}
                        dataProductId={dataProductId}
                        onDragStart={() => handleDragStart(dataOutput.id)}
                        onDragEnd={handleDragEnd}
                    />
                ))}

                {dataOutputs.length === 0 && (
                    <div className={styles.emptyState}>
                        <Typography.Text type="secondary">{t('No data outputs found')}</Typography.Text>
                    </div>
                )}
            </div>

            {isVisible && <AddDataOutputPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
