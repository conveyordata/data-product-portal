import { SafetyCertificateOutlined } from '@ant-design/icons';
import { Button, Flex, Popconfirm, Tooltip } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import AccessModesModal from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes-modal.tsx';
import { SettingsSectionHeader } from '@/pages/settings/components/settings-tabs/components/settings-section-header/settings-section-header.component.tsx';
import {
    type AccessModeWithType,
    useDeleteAccessModeMutation,
    useGetAccessModesQuery,
} from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { type UiElementMetadataResponse, useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

export default function AccessModes() {
    const { t } = useTranslation();
    const accessModesQuery = useGetAccessModesQuery();
    const { data: { access_modes = [] } = {} } = accessModesQuery;
    const sorter = new Sorter<AccessModeWithType>();
    const { data: { plugins = [] } = {} } = useGetPluginsQuery();
    const [deleteAccessMode, { isLoading: isDeleting }] = useDeleteAccessModeMutation();

    const technicalAssetTypeByPlugin = useMemo(() => {
        return new Map<string, string>(
            plugins.map((plugin: UiElementMetadataResponse) => [plugin.plugin, plugin.display_name]),
        );
    }, [plugins]);
    const technicalAssetTypeDisplayName = useCallback(
        (technicalAssetType: string) => technicalAssetTypeByPlugin.get(technicalAssetType) ?? t('Unknown'),
        [technicalAssetTypeByPlugin, t],
    );
    const technicalAssetTypeDisplayNames = useCallback(
        (technicalAssetTypes: string[] = []) =>
            technicalAssetTypes.map((technicalAssetType) => technicalAssetTypeDisplayName(technicalAssetType)),
        [technicalAssetTypeDisplayName],
    );
    const technicalAssetTypeFilters = useMemo(() => {
        const uniqueTechnicalAssetTypes = Array.from(
            new Set(access_modes.flatMap((accessMode) => accessMode.technical_asset_types ?? [])),
        ).sort();
        return uniqueTechnicalAssetTypes.map((technicalAssetType) => ({
            text: technicalAssetTypeDisplayName(technicalAssetType),
            value: technicalAssetType,
        }));
    }, [access_modes, technicalAssetTypeDisplayName]);
    const [openModal, setOpenModal] = useState<boolean>(false);
    const [editAccessMode, setEditAccessMode] = useState<AccessModeWithType | undefined>(undefined);

    const handleEdit = useCallback((accessMode: AccessModeWithType) => {
        setEditAccessMode(accessMode);
        setOpenModal(true);
    }, []);
    const cancelModal = useCallback(() => {
        setOpenModal(false);
        setEditAccessMode(undefined);
    }, []);

    const handleRemove = useCallback(
        async (accessMode: AccessModeWithType) => {
            try {
                await deleteAccessMode(accessMode.id).unwrap();
                dispatchMessage({ content: t('Access mode deleted successfully'), type: 'success' });
            } catch {
                // The request already showed its error.
            }
        },
        [deleteAccessMode, t],
    );
    const removeBlockedReason = (accessMode: AccessModeWithType) => {
        if (accessMode.in_use_technical_asset_types.length > 0) {
            return t('Technical Assets use this access mode');
        }
        const defaultTypesWithOtherAccessModes = accessMode.default_for_technical_asset_types.filter((type) =>
            access_modes.some((other) => other.id !== accessMode.id && other.technical_asset_types.includes(type)),
        );
        if (defaultTypesWithOtherAccessModes.length > 0) {
            return t('Make another access mode the default for {{types}} first', {
                types: technicalAssetTypeDisplayNames(defaultTypesWithOtherAccessModes).join(', '),
            });
        }
        return undefined;
    };

    return (
        <Flex vertical gap="medium">
            <SettingsSectionHeader
                title={t('Access Modes')}
                description={t('Configure available access modes for Technical Assets and Output Ports')}
                extra={
                    <Button type="primary" onClick={() => setOpenModal(true)}>
                        {t('Add Access Mode')}
                    </Button>
                }
            />
            <ListTable<AccessModeWithType>
                query={accessModesQuery}
                dataSource={access_modes}
                columns={[
                    {
                        title: t('Id'),
                        dataIndex: 'id',
                        hidden: true,
                    },
                    {
                        title: t('Name'),
                        dataIndex: 'name',
                        render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
                        width: '20%',
                        sorter: sorter.stringSorter((accessMode) => accessMode.name),
                    },
                    {
                        title: t('Technical Asset type'),
                        dataIndex: 'technical_asset_types',
                        render: (technical_asset_types: string[]) => {
                            const displayName = technicalAssetTypeDisplayNames(technical_asset_types).join(', ');
                            return <TableCellItem text={displayName} tooltip={{ content: displayName }} />;
                        },
                        filterSearch: true,
                        filters: technicalAssetTypeFilters,
                        onFilter: (value, record) =>
                            (record.technical_asset_types ?? []).includes(
                                typeof value === 'string' ? value : String(value),
                            ),
                        width: '20%',
                    },
                    {
                        title: t('Default for'),
                        dataIndex: 'default_for_technical_asset_types',
                        render: (default_for_technical_asset_types: string[]) => {
                            const displayName = technicalAssetTypeDisplayNames(default_for_technical_asset_types).join(
                                ', ',
                            );
                            return <TableCellItem text={displayName} tooltip={{ content: displayName }} />;
                        },
                        width: '20%',
                    },
                    {
                        title: t('Description'),
                        dataIndex: 'description',
                        render: (description: string) => (
                            <TableCellItem text={description} tooltip={{ content: description }} />
                        ),
                    },
                    {
                        title: t('Actions'),
                        key: 'action',
                        width: '10%',
                        render: (record: AccessModeWithType) => {
                            const blockedReason = removeBlockedReason(record);
                            return (
                                <Flex>
                                    <Button
                                        type="link"
                                        onClick={() => {
                                            handleEdit(record);
                                        }}
                                    >
                                        {t('Edit')}
                                    </Button>
                                    {blockedReason ? (
                                        <Tooltip title={blockedReason}>
                                            <Button type="link" disabled>
                                                {t('Remove')}
                                            </Button>
                                        </Tooltip>
                                    ) : (
                                        <Popconfirm
                                            title={t('Remove')}
                                            description={t('Are you sure you want to delete this access mode?')}
                                            onConfirm={() => handleRemove(record)}
                                            placement="leftTop"
                                            okText={t('Confirm')}
                                            cancelText={t('Cancel')}
                                            okButtonProps={{ loading: isDeleting }}
                                            autoAdjustOverflow={true}
                                        >
                                            <Button loading={isDeleting} disabled={isDeleting} type="link">
                                                {t('Remove')}
                                            </Button>
                                        </Popconfirm>
                                    )}
                                </Flex>
                            );
                        },
                    },
                ]}
                subject={t('Access Modes')}
                emptyState={{
                    icon: <SafetyCertificateOutlined />,
                    title: t('No Access Modes yet'),
                    description: t('Access Modes describe how people may use the data they are granted.'),
                }}
                rowKey={(record) => record.id}
                pagination={{ hideOnSinglePage: true }}
                size="small"
            />
            {openModal && <AccessModesModal onClose={cancelModal} editAccessMode={editAccessMode} />}
        </Flex>
    );
}
