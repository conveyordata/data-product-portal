import { Button, Flex, Table, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import {
    OutputPortAccessFunction,
    type OutputPortClassificationsGetItem,
    useGetOutputPortClassificationsQuery,
    useRemoveOutputPortClassificationMutation,
} from '@/store/api/services/generated/configurationOutputPortClassificationsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { OutputPortClassificationFormModal } from './output-port-classification-form-modal.component.tsx';
import { getOutputPortClassificationsTableColumns } from './output-port-classifications-table-columns.tsx';

export function OutputPortClassificationsTable() {
    const { t } = useTranslation();
    const { data, isFetching } = useGetOutputPortClassificationsQuery();
    const { isVisible, handleOpen, handleClose } = useModal();
    const [initial, setInitial] = useState<OutputPortClassificationsGetItem | undefined>(undefined);
    const [removeClassification] = useRemoveOutputPortClassificationMutation();
    const inviteOnlyClassifications = data?.output_port_classifications.filter(
        (classification) => classification.access_function === OutputPortAccessFunction.Private,
    );
    const lastInviteOnlyId = inviteOnlyClassifications?.length === 1 ? inviteOnlyClassifications[0].id : undefined;

    const handleAdd = () => {
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = useCallback(
        (classification: OutputPortClassificationsGetItem) => () => {
            setInitial(classification);
            handleOpen();
        },
        [handleOpen],
    );

    const handleRemove = useCallback(
        async (classification: OutputPortClassificationsGetItem) => {
            try {
                await removeClassification(classification.id).unwrap();
                dispatchMessage({ content: t('Classification removed successfully'), type: 'success' });
            } catch (_) {
                dispatchMessage({ content: t('Could not remove classification'), type: 'error' });
            }
        },
        [t, removeClassification],
    );

    const columns = useMemo(
        () => getOutputPortClassificationsTableColumns({ t, handleEdit, handleRemove, lastInviteOnlyId }),
        [t, handleEdit, handleRemove, lastInviteOnlyId],
    );

    return (
        <Flex vertical gap="large">
            <Flex justify="space-between" align="center">
                <Typography.Title level={3}>{t('Classifications')}</Typography.Title>
                <Button type="primary" onClick={handleAdd}>
                    {t('Add Classification')}
                </Button>
            </Flex>
            <Table<OutputPortClassificationsGetItem>
                dataSource={data?.output_port_classifications}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                size="small"
            />
            {isVisible && (
                <OutputPortClassificationFormModal
                    onClose={handleClose}
                    initial={initial}
                    isLastInviteOnly={initial !== undefined && initial.id === lastInviteOnlyId}
                />
            )}
        </Flex>
    );
}
