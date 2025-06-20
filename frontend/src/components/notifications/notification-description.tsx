import { Button, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import type { EventContract } from '@/types/events/event.contract';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { getEventReferenceEntityLinkPath, getSubjectDisplayLabel, getTargetDisplayLabel } from '@/utils/history.helper';
import { getEventTypeNotificationText } from '@/utils/notification.helper';

import styles from './notifications.module.scss';

interface NotificationDescriptionProps {
    record: EventContract;
}

export function NotificationDescription({ record }: NotificationDescriptionProps): ReactNode | null {
    const { target_id, subject_id, subject_type, target_type, deleted_subject_identifier, deleted_target_identifier } =
        record;
    const { t } = useTranslation();
    const navigate = useNavigate();

    const subjectButton = (() => {
        const subjectPath = getEventReferenceEntityLinkPath(
            subject_id,
            subject_type === EventReferenceEntity.DataOutput ? (record.data_output?.owner_id ?? null) : null,
            subject_type,
        );

        return subject_type === EventReferenceEntity.User ? (
            <Typography.Text>{getSubjectDisplayLabel(t, record)}</Typography.Text>
        ) : (
            <Button
                type="link"
                disabled={!!deleted_subject_identifier}
                className={styles.eventLink}
                onClick={(e) => {
                    e.preventDefault();
                    if (subjectPath) navigate(subjectPath);
                }}
            >
                {getSubjectDisplayLabel(t, record)}
            </Button>
        );
    })();

    const targetButton = target_id
        ? (() => {
              const targetPath = getEventReferenceEntityLinkPath(
                  target_id,
                  target_type === EventReferenceEntity.DataOutput ? (record.data_output?.owner_id ?? null) : null,
                  target_type,
              );

              return target_type === EventReferenceEntity.User ? (
                  <Typography.Text>{getTargetDisplayLabel(t, record)}</Typography.Text>
              ) : (
                  <Button
                      type="link"
                      disabled={!!deleted_target_identifier}
                      className={styles.eventLink}
                      onClick={(e) => {
                          e.preventDefault();
                          if (targetPath) navigate(targetPath);
                      }}
                  >
                      {getTargetDisplayLabel(t, record)}
                  </Button>
              );
          })()
        : null;

    return (
        <Typography.Text>
            {subjectButton} {getEventTypeNotificationText(t, record.name)} {targetButton}
        </Typography.Text>
    );
}
