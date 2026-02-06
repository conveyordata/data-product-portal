import { Button, Flex, Input, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TechnicalAssetCard } from '@/components/data-outputs/technical-asset-card/data-output-card.component.tsx';
import { useModal } from '@/hooks/use-modal.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetDataProductTechnicalAssetsQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { AddDataOutputPopup } from '../add-data-output-popup/add-data-output-popup.tsx';

type Props = {
    dataProductId: string;
    onDragStart?: (dataOutputId: string) => void;
    onDragEnd?: () => void;
};

export function TechnicalAssetsTable({ dataProductId, onDragStart, onDragEnd }: Props) {
    const { t } = useTranslation();
    const { data: { technical_assets: technicalAssets = [] } = {} } =
        useGetDataProductTechnicalAssetsQuery(dataProductId);
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductQuery(dataProductId);
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
        },
        { skip: !dataProductId },
    );
    const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);

    const filteredDataOutputs = useMemo(() => {
        if (!searchTerm) return technicalAssets;
        return technicalAssets.filter(
            (dataOutput) =>
                dataOutput?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataOutput?.namespace?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                dataOutput?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        );
    }, [technicalAssets, searchTerm]);

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

                <Input.Search
                    placeholder={t('Search Technical Assets by name or namespace')}
                    allowClear
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </Flex>

            {filteredDataOutputs.map((technicalAsset) => (
                <TechnicalAssetCard
                    key={technicalAsset.id}
                    technicalAsset={technicalAsset}
                    dataProductId={dataProductId}
                    onDragStart={() => handleDragStart(technicalAsset.id)}
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
