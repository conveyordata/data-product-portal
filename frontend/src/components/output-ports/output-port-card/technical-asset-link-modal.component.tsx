import { Button, Checkbox, Flex, Input, List, Modal, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { NotShareableIcon } from '@/components/technical-assets/not-shareable-icon/not-shareable-icon.component.tsx';
import { DATA_OUTPUTS_TABLE_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import type { TechnicalAssetLink } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    useApproveOutputPortTechnicalAssetLinkMutation,
    useGetDataProductTechnicalAssetsQuery,
    useLinkOutputPortToTechnicalAssetMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { isTechnicalAssetNotShareableError } from '@/store/common/api-errors.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { getTechnicalAssetIcon, isTechnicalAssetShareable } from '@/utils/technical-asset-type.helper.ts';

type Props = {
    onClose: () => void;
    dataProductId: string;
    datasetId: string;
    datasetName: string;
    existingLinks: TechnicalAssetLink[];
};

export function TechnicalAssetLinkModal({ onClose, dataProductId, datasetId, datasetName, existingLinks }: Props) {
    const { t } = useTranslation();
    const [selectedOutputs, setSelectedOutputs] = useState<Set<string>>(new Set());

    const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
    const { data: { plugins } = {} } = useGetPluginsQuery();
    const [linkDatasets, { isLoading: isLinking }] = useLinkOutputPortToTechnicalAssetMutation();
    const [approveLink] = useApproveOutputPortTechnicalAssetLinkMutation();

    const { data: { technical_assets: technicalAssets = [] } = {} } = useGetDataProductTechnicalAssetsQuery(
        dataProductId,
        { skip: !dataProductId },
    );

    const existingLinkIds = useMemo(() => {
        return new Set(existingLinks.map((link) => link.technical_asset_id));
    }, [existingLinks]);

    const availableDataOutputs = useMemo(() => {
        return technicalAssets.filter((output) => !existingLinkIds.has(output.id));
    }, [technicalAssets, existingLinkIds]);

    const filteredDataOutputs = useMemo(() => {
        if (!searchTerm) return availableDataOutputs;
        return availableDataOutputs.filter(
            (output) =>
                output.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                output.namespace.toLowerCase().includes(searchTerm.toLowerCase()),
        );
    }, [availableDataOutputs, searchTerm]);

    const selectableDataOutputs = useMemo(
        () =>
            plugins
                ? filteredDataOutputs.filter((output) => isTechnicalAssetShareable(output.configuration.name, plugins))
                : [],
        [filteredDataOutputs, plugins],
    );

    const allSelected = selectableDataOutputs.length > 0 && selectedOutputs.size === selectableDataOutputs.length;

    const { pagination, handleCurrentPageChange } = useTablePagination(filteredDataOutputs, {
        initialPagination: DATA_OUTPUTS_TABLE_PAGINATION,
    });

    const handleOutputToggle = (outputId: string) => {
        setSelectedOutputs((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(outputId)) {
                newSet.delete(outputId);
            } else {
                newSet.add(outputId);
            }
            return newSet;
        });
    };

    const handleSelectAll = () => {
        if (allSelected) {
            setSelectedOutputs(new Set());
        } else {
            setSelectedOutputs(new Set(selectableDataOutputs.map((output) => output.id)));
        }
    };

    const handleSubmit = async () => {
        try {
            const linkPromises = Array.from(selectedOutputs).map(async (outputId) => {
                const result = await linkDatasets({
                    dataProductId,
                    outputPortId: datasetId,
                    linkTechnicalAssetToOutputPortRequest: {
                        technical_asset_id: outputId,
                    },
                }).unwrap();
                await approveLink({
                    dataProductId,
                    outputPortId: datasetId,
                    approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                        technical_asset_id: outputId,
                    },
                }).unwrap();
                return result;
            });

            await Promise.all(linkPromises);

            dispatchMessage({
                content: t('{{count}} Technical Assets linked successfully', { count: selectedOutputs.size }),
                type: 'success',
            });

            setSelectedOutputs(new Set());
            onClose();
        } catch (error) {
            if (isTechnicalAssetNotShareableError(error)) {
                dispatchMessage({
                    content: t(
                        "You can't link these Technical Assets to an Output Port because one of their types is not shareable",
                    ),
                    type: 'error',
                });
                return;
            }
            dispatchMessage({
                content: t('Failed to link Technical Assets'),
                type: 'error',
            });
        }
    };

    return (
        <Modal
            title={t('Link Technical Assets to {{name}}', { name: datasetName })}
            open
            onCancel={onClose}
            width={600}
            footer={[
                <Button key="cancel" onClick={onClose}>
                    {t('Cancel')}
                </Button>,
                <Button
                    key="submit"
                    type="primary"
                    onClick={handleSubmit}
                    loading={isLinking}
                    disabled={selectedOutputs.size === 0}
                >
                    {t('Link {{count}} assets', { count: selectedOutputs.size })}
                </Button>,
            ]}
        >
            <Input.Search
                placeholder={t('Search Technical Assets')}
                allowClear
                onChange={(e) => setSearchTerm(e.target.value)}
            />

            {filteredDataOutputs.length > 0 && (
                <Flex justify="space-between" align="center">
                    <Typography.Text type="secondary">
                        {t('{{count}} available Technical Assets', { count: filteredDataOutputs.length })}
                    </Typography.Text>
                    <Button type="link" onClick={handleSelectAll} disabled={selectableDataOutputs.length === 0}>
                        {allSelected ? t('Deselect All') : t('Select All')}
                    </Button>
                </Flex>
            )}
            <List
                style={{ width: '100%' }}
                dataSource={filteredDataOutputs}
                pagination={{
                    ...pagination,
                    size: 'small',
                    position: 'bottom',
                    showTotal: (total: number, range: [number, number]) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Technical Assets', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                    onChange: handleCurrentPageChange,
                }}
                locale={{ emptyText: t('No Technical Assets available') }}
                renderItem={(output) => {
                    const shareable = isTechnicalAssetShareable(output.configuration.name, plugins);
                    return (
                        <List.Item data-cy="technical-asset-link-item">
                            <Flex align="center" gap={12} style={{ width: '100%' }}>
                                <Checkbox
                                    checked={selectedOutputs.has(output.id)}
                                    disabled={!plugins || !shareable}
                                    onChange={() => handleOutputToggle(output.id)}
                                />
                                <CustomSvgIconLoader
                                    iconComponent={getTechnicalAssetIcon(output.configuration.name, plugins)}
                                />
                                <Flex vertical style={{ flex: 1 }}>
                                    <Flex gap="small" align="center">
                                        <Typography.Text strong disabled={!shareable}>
                                            {output.result_string}
                                        </Typography.Text>
                                        {!shareable && <NotShareableIcon iconOnly />}
                                    </Flex>
                                    <Typography.Text type="secondary">{output.name}</Typography.Text>
                                </Flex>
                            </Flex>
                        </List.Item>
                    );
                }}
            />
        </Modal>
    );
}
