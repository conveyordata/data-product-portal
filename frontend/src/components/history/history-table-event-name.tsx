import { Button, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import type { EventContract } from '@/types/events/event.contract';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import {
    getEventReferenceEntityLinkPath,
    getEventTypeDisplayName,
    getSubjectDisplayLabel,
    getTargetDisplayLabel,
} from '@/utils/history.helper';

interface HistoryTableLinkProps {
    record: EventContract;
    resourceId: string;
    type: EventReferenceEntity;
}

export function HistoryTableEventName({ record, resourceId, type }: HistoryTableLinkProps): ReactNode {
    const { target_id, subject_id, subject_type, target_type, deleted_subject_identifier, deleted_target_identifier } =
        record;
    const { t } = useTranslation();
    const navigate = useNavigate();

    if (!(subject_id === resourceId && type === subject_type)) {
        const path = getEventReferenceEntityLinkPath(
            subject_id,
            subject_type === EventReferenceEntity.DataOutput ? (record.data_output?.owner_id ?? null) : null,
            subject_type,
        );

        if (subject_type === EventReferenceEntity.User) {
            return (
                <Typography.Text>
                    {getEventTypeDisplayName(t, record.name)} {getTargetDisplayLabel(t, record)}
                </Typography.Text>
            );
        }
        return (
            <Typography.Text>
                {getEventTypeDisplayName(t, record.name)}{' '}
                <Button
                    type="link"
                    disabled={!!deleted_subject_identifier}
                    style={{ paddingLeft: 0 }}
                    onClick={() => {
                        if (path) navigate(path);
                    }}
                >
                    {getSubjectDisplayLabel(t, record)}
                </Button>
            </Typography.Text>
        );
    }

    if (target_id && !(target_id === resourceId && type === target_type)) {
        const path = getEventReferenceEntityLinkPath(
            target_id,
            target_type === EventReferenceEntity.DataOutput ? (record.data_output?.owner_id ?? null) : null,
            target_type,
        );

        if (target_type === EventReferenceEntity.User) {
            return (
                <Typography.Text>
                    {getEventTypeDisplayName(t, record.name)} {getTargetDisplayLabel(t, record)}
                </Typography.Text>
            );
        }
        return (
            <Typography.Text>
                {getEventTypeDisplayName(t, record.name)}{' '}
                <Button
                    type="link"
                    disabled={!!deleted_target_identifier}
                    style={{ paddingLeft: 0 }}
                    onClick={() => {
                        if (path) navigate(path);
                    }}
                >
                    {getTargetDisplayLabel(t, record)}
                </Button>
            </Typography.Text>
        );
    }

    return <Typography.Text>{getEventTypeDisplayName(t, record.name)}</Typography.Text>;
}
