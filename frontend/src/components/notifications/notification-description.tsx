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
    getNotificationDisplayName,
    getSubjectDisplayLabel,
    getTargetDisplayLabel,
} from '@/utils/history.helper';

interface NotificationDescriptionProps {
    record: GetEventHistoryResponseItem;
}

export function NotificationDescription({ record }: NotificationDescriptionProps): ReactNode | null {
    const { target_id, subject_id, subject_type, target_type, deleted_subject_identifier, deleted_target_identifier } =
        record;
    const { t } = useTranslation();
    const navigate = useNavigate();

    const subjectPath = getEventReferenceEntityLinkPath(
        subject_id,
        subject_type === EventEntityType.TechnicalAsset
            ? (record.technical_asset?.owner_id ?? null)
            : subject_type === EventEntityType.OutputPort
              ? (record.output_port?.data_product_id ?? null)
              : null,
        subject_type,
    );
    let subjectelement = <></>;
    if (subject_type !== EventReferenceEntity.User) {
        subjectelement = (
            <Button
                type="link"
                disabled={!!deleted_subject_identifier}
                style={{ padding: 0 }}
                onClick={() => {
                    if (subjectPath) navigate(subjectPath);
                }}
            />
        );
    }
    let targetelement = <></>;
    if (target_id) {
        const targetPath = getEventReferenceEntityLinkPath(
            target_id,
            target_type === EventEntityType.TechnicalAsset
                ? (record.technical_asset?.owner_id ?? null)
                : target_type === EventEntityType.OutputPort
                  ? (record.output_port?.data_product_id ?? null)
                  : null,
            target_type,
        );
        if (target_type !== EventReferenceEntity.User) {
            targetelement = (
                <Button
                    type="link"
                    disabled={!!deleted_target_identifier}
                    style={{ padding: 0 }}
                    onClick={() => {
                        if (targetPath) navigate(targetPath);
                    }}
                />
            );
        }
    }
    return (
        <Typography.Text>
            {getNotificationDisplayName(
                t,
                parseEventType(record.name),
                record.subject_type,
                getSubjectDisplayLabel(record),
                record.target_type,
                getTargetDisplayLabel(record),
                subjectelement,
                targetelement,
            )}
        </Typography.Text>
    );
}
