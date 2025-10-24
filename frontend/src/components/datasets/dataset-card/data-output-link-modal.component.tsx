import { Button, Checkbox, Flex, Form, List, Modal, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { DATA_OUTPUTS_TABLE_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useRequestDatasetAccessForDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useApproveDataOutputLinkMutation } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import type { SearchForm } from '@/types/shared';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';

type Props = {
    onClose: () => void;
    datasetId: string;
    datasetName: string;
    existingLinks: Array<{ data_output: { id: string; name: string } }>;
};

export function DataOutputLinkModal({ onClose, datasetId, datasetName, existingLinks }: Props) {
    const { t } = useTranslation();
    const [selectedOutputs, setSelectedOutputs] = useState<Set<string>>(new Set());

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const { data: dataset } = useGetDatasetByIdQuery(datasetId);

    const [linkDataset, { isLoading: isLinking }] = useRequestDatasetAccessForDataOutputMutation();
    const [approveLink] = useApproveDataOutputLinkMutation();

    const dataProductId = dataset?.data_product_id || '';
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });

    const existingLinkIds = useMemo(() => {
        return new Set(existingLinks.map((link) => link.data_output.id));
    }, [existingLinks]);

    const availableDataOutputs = useMemo(() => {
        if (!dataProduct?.data_outputs) return [];
        return dataProduct.data_outputs.filter((output) => !existingLinkIds.has(output.id));
    }, [dataProduct?.data_outputs, existingLinkIds]);

    const filteredDataOutputs = useMemo(() => {
        if (!searchTerm) return availableDataOutputs;
        return availableDataOutputs.filter(
            (output) =>
                output.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                output.namespace.toLowerCase().includes(searchTerm.toLowerCase()),
        );
    }, [availableDataOutputs, searchTerm]);

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
        if (selectedOutputs.size === filteredDataOutputs.length) {
            setSelectedOutputs(new Set());
        } else {
            setSelectedOutputs(new Set(filteredDataOutputs.map((output) => output.id)));
        }
    };

    const handleSubmit = async () => {
        try {
            const linkPromises = Array.from(selectedOutputs).map(async (outputId) => {
                const result = await linkDataset({ dataOutputId: outputId, datasetId }).unwrap();
                await approveLink({ id: result.id, data_output_id: outputId, dataset_id: datasetId }).unwrap();
                return result;
            });

            await Promise.all(linkPromises);

            dispatchMessage({
                content: t('{{count}} technical assets linked successfully', { count: selectedOutputs.size }),
                type: 'success',
            });

            setSelectedOutputs(new Set());
            onClose();
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to link technical assets'),
                type: 'error',
            });
        }
    };

    return (
        <Modal
            title={t('Link technical assets to {{name}}', { name: datasetName })}
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
            <Searchbar
                form={searchForm}
                placeholder={t('Search technical assets')}
                formItemProps={{ initialValue: '' }}
            />

            {filteredDataOutputs.length > 0 && (
                <Flex justify="space-between" align="center">
                    <Typography.Text type="secondary">
                        {t('{{count}} available technical assets', { count: filteredDataOutputs.length })}
                    </Typography.Text>
                    <Button type="link" onClick={handleSelectAll}>
                        {selectedOutputs.size === filteredDataOutputs.length ? t('Deselect All') : t('Select All')}
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
                        t('Showing {{range0}}-{{range1}} of {{total}} technical assets', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    onChange: handleCurrentPageChange,
                }}
                locale={{ emptyText: t('No technical assets available') }}
                renderItem={(output) => (
                    <List.Item>
                        <Flex align="center" gap={12} style={{ width: '100%' }}>
                            <Checkbox
                                checked={selectedOutputs.has(output.id)}
                                onChange={() => handleOutputToggle(output.id)}
                            />
                            <CustomSvgIconLoader
                                iconComponent={getDataOutputIcon(output.configuration.configuration_type)}
                            />
                            <Flex vertical style={{ flex: 1 }}>
                                <Typography.Text strong>{output.result_string}</Typography.Text>
                                <Typography.Text type="secondary">{output.name}</Typography.Text>
                            </Flex>
                        </Flex>
                    </List.Item>
                )}
            />
        </Modal>
    );
}
