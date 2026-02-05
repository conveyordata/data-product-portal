import { Button, Flex, Form, Typography } from 'antd';
import { useMemo } from 'react';
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
    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
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
        onDragStart?.(dataOutputId);
    };

    const handleDragEnd = () => {
        onDragEnd?.();
    };

    return (
        <Flex vertical gap={filteredDataOutputs.length === 0 ? 'large' : 'small'}>
            <Flex vertical gap="middle">
                <Flex justify="space-between" align="center">
                    <Typography.Title level={4} style={{ margin: 0 }}>
                        {t('Technical Assets')}
                    </Typography.Title>
                    <Button
                        disabled={!canCreateDataOutput}
                        type="primary"
                        loading={isLoadingDataProduct}
                        onClick={handleOpen}
                    >
                        {t('Add Technical Asset')}
                    </Button>
                </Flex>

                <Searchbar
                    placeholder={t('Search Technical Assets by name or namespace')}
                    formItemProps={{ initialValue: '', className: styles.searchBar }}
                    form={searchForm}
                />
            </Flex>

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
                <Flex justify={'center'}>
                    <Typography.Text type="secondary">
                        {searchTerm
                            ? t('No Technical Assets found matching your search')
                            : t('No Technical Assets found')}
                    </Typography.Text>
                </Flex>
            )}

            {isVisible && <AddDataOutputPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </Flex>
    );
}
