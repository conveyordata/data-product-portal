import { Button, Flex, Popconfirm, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import AccessModesModal from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes-modal.tsx';
import {
    type AccessModeWithType,
    useDeleteAccessModeMutation,
    useGetAccessModesQuery,
} from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { type UiElementMetadataResponse, useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi.ts';
import {
    CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR,
    isCanNotRemoveAccessModeInUseError,
} from '@/store/common/api-errors.ts';
import { showGenericErrorMessage } from '@/store/common/errors.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

export default function AccessModes() {
    const { t } = useTranslation();
    const { data: { access_modes = [] } = {}, isFetching } = useGetAccessModesQuery();
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
            } catch (error) {
                if (isCanNotRemoveAccessModeInUseError(error)) {
                    dispatchMessage({ content: t(CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR), type: 'error' });
                } else {
                    showGenericErrorMessage(error);
                }
            }
        },
        [deleteAccessMode, t],
    );

    return (
        <>
            <Flex vertical gap="small">
                <Flex justify="space-between" align="center">
                    <Typography.Title level={3}>{t('Access modes')}</Typography.Title>
                    <Button type="primary" onClick={() => setOpenModal(true)}>
                        {t('Add access mode')}
                    </Button>
                </Flex>
                <Typography.Text type="secondary">
                    {t('Configure available access modes for Technical Assets and Output Ports')}
                </Typography.Text>
            </Flex>
            <Table<AccessModeWithType>
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
                        width: '25%',
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
                                </Flex>
                            );
                        },
                    },
                ]}
                rowKey={(record) => record.id}
                loading={isFetching}
                size="small"
            />
            {openModal && <AccessModesModal onClose={cancelModal} editAccessMode={editAccessMode} />}
        </>
    );
}
