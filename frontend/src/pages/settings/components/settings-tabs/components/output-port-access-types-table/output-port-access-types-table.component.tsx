import { Button, Flex, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
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
    const { data, isFetching } = useGetOutputPortAccessTypesQuery();
    const { isVisible, handleOpen, handleClose } = useModal();
    const [initial, setInitial] = useState<OutputPortAccessTypesGetItem | undefined>(undefined);
    const [removeAccessType] = useRemoveOutputPortAccessTypeMutation();
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
        () => getOutputPortAccessTypesTableColumns({ t, handleEdit, handleRemove, lastInviteOnlyId }),
        [t, handleEdit, handleRemove, lastInviteOnlyId],
    );

    return (
        <Flex vertical gap="large">
            <Flex justify="space-between" align="center">
                <Typography.Title level={3}>{t('Access Types')}</Typography.Title>
                <Button type="primary" onClick={handleAdd}>
                    {t('Add Access Type')}
                </Button>
            </Flex>
            <Table<OutputPortAccessTypesGetItem>
                dataSource={data?.output_port_access_types}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching}
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
