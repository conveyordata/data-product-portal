import { Button, Flex, Input, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { searchFilter } from '@/components/empty-state/empty-state.component.tsx';
import { TechnicalAssetOutlined } from '@/components/icons';
import { QueryList } from '@/components/query-list/query-list.component.tsx';
import { TechnicalAssetCard } from '@/components/technical-assets/technical-asset-card/technical-asset-card.component.tsx';
import { useModal } from '@/hooks/use-modal.tsx';
import { AddTechnicalAssetPopup } from '@/pages/data-product/components/data-product-tabs/technical-asset-tab/components/add-technical-asset-popup/add-technical-asset-popup.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetDataProductTechnicalAssetsQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';

type Props = {
    dataProductId: string;
    onDragStart?: (dataOutputId: string) => void;
    onDragEnd?: () => void;
};

export function TechnicalAssetsTable({ dataProductId, onDragStart, onDragEnd }: Props) {
    const { t } = useTranslation();
    const technicalAssetsQuery = useGetDataProductTechnicalAssetsQuery(dataProductId);
    const { data: { technical_assets: technicalAssets = [] } = {} } = technicalAssetsQuery;
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductQuery(dataProductId);
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
        },
        { skip: !dataProductId },
    );
    const [searchTerm, setSearchTerm] = useState('');

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
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </Flex>

            <QueryList
                query={technicalAssetsQuery}
                items={filteredDataOutputs}
                renderItem={(technicalAsset) => (
                    <TechnicalAssetCard
                        key={technicalAsset.id}
                        technicalAsset={technicalAsset}
                        dataProductId={dataProductId}
                        onDragStart={() => handleDragStart(technicalAsset.id)}
                        onDragEnd={handleDragEnd}
                    />
                )}
                subject={t('Technical Assets')}
                emptyState={{
                    icon: <TechnicalAssetOutlined />,
                    title: t('No Technical Assets yet'),
                    description: t('Add a Technical Asset to describe where the data of this Data Product lives.'),
                }}
                filter={searchFilter(searchTerm, setSearchTerm)}
            />

            {isVisible && (
                <AddTechnicalAssetPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />
            )}
        </Flex>
    );
}
