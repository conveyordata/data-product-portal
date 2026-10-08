import { Button, Flex, Table } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useModal } from '@/hooks/use-modal.tsx';
import { SettingsSectionHeader } from '@/pages/settings/components/settings-tabs/components/settings-section-header/settings-section-header.component.tsx';
import {
    OutputPortAccessFunction,
    type OutputPortAccessTypesGetItem,
    useGetOutputPortAccessTypesQuery,
    useRemoveOutputPortAccessTypeMutation,
} from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { OutputPortAccessTypeFormModal } from './output-port-access-type-form-modal.component.tsx';
import { getOutputPortAccessTypesTableColumns } from './output-port-access-types-table-columns.tsx';

export function OutputPortAccessTypesTable() {
    const { t } = useTranslation();
    const { data, isFetching } = useGetOutputPortAccessTypesQuery(true);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [initial, setInitial] = useState<OutputPortAccessTypesGetItem>();
    const [removeAccessType, { isLoading: isRemoving }] = useRemoveOutputPortAccessTypeMutation();
    const inviteOnlyAccessTypes = data?.output_port_access_types.filter(
        (accessType) => accessType.access_function === OutputPortAccessFunction.Private,
    );
    const lastInviteOnlyId = inviteOnlyAccessTypes?.length === 1 ? inviteOnlyAccessTypes[0].id : undefined;

    const handleAdd = () => {
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = useCallback(
        (accessType: OutputPortAccessTypesGetItem) => () => {
            setInitial(accessType);
            handleOpen();
        },
        [handleOpen],
    );

    const handleRemove = useCallback(
        async (accessType: OutputPortAccessTypesGetItem) => {
            const result = await removeAccessType(accessType.id);
            if (!result.error) {
                dispatchMessage({ content: t('Access Type removed successfully'), type: 'success' });
            }
        },
        [t, removeAccessType],
    );

    const columns = useMemo(
        () => getOutputPortAccessTypesTableColumns({ t, handleEdit, handleRemove, lastInviteOnlyId, isRemoving }),
        [t, handleEdit, handleRemove, lastInviteOnlyId, isRemoving],
    );

    return (
        <Flex vertical gap="middle">
            <SettingsSectionHeader
                title={t('Access Types')}
                description={t('Configure how openly Output Ports can be shared and whether access needs approval.')}
                extra={
                    <Button type="primary" onClick={handleAdd}>
                        {t('Add Access Type')}
                    </Button>
                }
            />
            <Table<OutputPortAccessTypesGetItem>
                dataSource={data?.output_port_access_types}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching}
                pagination={{ hideOnSinglePage: true }}
                rowHoverable
                size="small"
            />
            {isVisible && (
                <OutputPortAccessTypeFormModal
                    onClose={handleClose}
                    initial={initial}
                    isLastInviteOnly={initial !== undefined && initial.id === lastInviteOnlyId}
                />
            )}
        </Flex>
    );
}
