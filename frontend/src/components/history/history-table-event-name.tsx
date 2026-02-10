import { Button, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import {
    EventEntityType,
    type GetEventHistoryResponseItem,
} from '@/store/api/services/generated/usersNotificationsApi.ts';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { parseEventType } from '@/types/events/event-types.ts';
import {
    getEventReferenceEntityLinkPath,
    getEventTypeDisplayName,
    getSubjectDisplayLabel,
    getTargetDisplayLabel,
} from '@/utils/history.helper';

interface HistoryTableLinkProps {
    record: GetEventHistoryResponseItem;
    resourceId: string;
    type: EventReferenceEntity;
}

export function HistoryTableEventName({ record, resourceId, type }: HistoryTableLinkProps): ReactNode {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { target_id, subject_id, subject_type, target_type, deleted_subject_identifier, deleted_target_identifier } =
        record;
    if (!(subject_id === resourceId && type === subject_type)) {
        const path = getEventReferenceEntityLinkPath(
            subject_id,
            subject_type === EventEntityType.TechnicalAsset
                ? (record.technical_asset?.owner_id ?? null)
                : subject_type === EventEntityType.OutputPort
                  ? (record.output_port?.data_product_id ?? null)
                  : null,
            subject_type,
        );

        let element = <></>;
        if (subject_type !== EventReferenceEntity.User) {
            element = (
                <Button
                    type="link"
                    disabled={!!deleted_subject_identifier}
                    style={{ padding: 0 }}
                    onClick={() => {
                        if (path) navigate(path);
                    }}
                />
            );
        }
        return (
            <Typography.Text>
                {getEventTypeDisplayName(
                    t,
                    parseEventType(record.name),
                    record.subject_type,
                    getSubjectDisplayLabel(record),
                    element,
                )}
            </Typography.Text>
        );
    }

    if (target_id && !(target_id === resourceId && type === target_type)) {
        const path = getEventReferenceEntityLinkPath(
            target_id,
            target_type === EventEntityType.TechnicalAsset
                ? (record.technical_asset?.owner_id ?? null)
                : target_type === EventEntityType.OutputPort
                  ? (record.output_port?.data_product_id ?? null)
                  : null,
            target_type,
        );

        let element = <></>;
        if (target_type !== EventReferenceEntity.User) {
            element = (
                <Button
                    type="link"
                    disabled={!!deleted_target_identifier}
                    style={{ padding: 0 }}
                    onClick={() => {
                        if (path) navigate(path);
                    }}
                />
            );
        }
        return (
            <Typography.Text>
                {getEventTypeDisplayName(
                    t,
                    parseEventType(record.name),
                    record.target_type,
                    getTargetDisplayLabel(record),
                    element,
                )}
            </Typography.Text>
        );
    }
    return (
        <Typography.Text>
            {getEventTypeDisplayName(t, parseEventType(record.name), undefined, '', <div />)}
        </Typography.Text>
    );
}
