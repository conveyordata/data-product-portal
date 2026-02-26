import type { TFunction } from 'i18next';
import type { ReactElement, ReactNode } from 'react';
import { Trans } from 'react-i18next';
import { EventEntityType, type GetEventHistoryResponseItem } from '@/store/api/services/generated/dataProductsApi.ts';
import { EventType } from '@/types/events/event-types';
import { createDataOutputIdPath, createDataProductIdPath, createMarketplaceOutputPortPath } from '@/types/navigation';

export function getTypeDisplayName(t: TFunction, type: EventEntityType | undefined | null): string {
    switch (type) {
        case EventEntityType.OutputPort:
            return t('Output Port');
        case EventEntityType.DataProduct:
            return t('Data Product');
        case EventEntityType.TechnicalAsset:
            return t('Technical Asset');
        case EventEntityType.User:
            return t('User');
        default:
            return t('Unknown');
    }
}

export function getSubjectDisplayLabel(record: GetEventHistoryResponseItem): string {
    const { subject_type, deleted_subject_identifier } = record;

    if (deleted_subject_identifier) {
        return deleted_subject_identifier;
    }

    switch (subject_type) {
        case EventEntityType.User:
            return record.user?.email || '';
        case EventEntityType.DataProduct:
            return record.data_product?.name || '';
        case EventEntityType.TechnicalAsset:
            return record.technical_asset?.name || '';
        case EventEntityType.OutputPort:
            return record.output_port?.name || '';
    }
}

export function getTargetDisplayLabel(record: GetEventHistoryResponseItem): string {
    const { target_type, deleted_target_identifier } = record;

    if (deleted_target_identifier) {
        return deleted_target_identifier || '';
    }

    switch (target_type) {
        case EventEntityType.User:
            return record.user?.email || '';
        case EventEntityType.DataProduct:
            return record.data_product?.name || '';
        case EventEntityType.TechnicalAsset:
            return record.technical_asset?.name || '';
        case EventEntityType.OutputPort:
            return record.output_port?.name || '';
        default:
            return '';
    }
}

export function getEventReferenceEntityLinkPath(
    id: string,
    dataProductId: string | null,
    type: EventEntityType | null | undefined,
): string | null {
    switch (type) {
        case EventEntityType.OutputPort:
            return dataProductId ? createMarketplaceOutputPortPath(id, dataProductId) : null;
        case EventEntityType.DataProduct:
            return createDataProductIdPath(id);
        case EventEntityType.TechnicalAsset:
            return dataProductId ? createDataOutputIdPath(id, dataProductId) : null;
        case EventEntityType.User:
            return null;
        default:
            return null;
    }
}

export function getEventTypeDisplayName(
    t: TFunction,
    event_type: EventType,
    entity_reference: EventEntityType | undefined | null,
    entity: string,
    element: ReactElement,
): ReactNode {
    const entity_type = getTypeDisplayName(t, entity_reference);

    switch (event_type) {
        case EventType.DATA_OUTPUT_CREATED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataOutputCreated"
                    defaults="Technical Asset created: now linked with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_OUTPUT_UPDATED:
            return <Trans t={t} i18nKey="EventDataOutputUpdated" defaults="Technical Asset updated" />;
        case EventType.DATA_OUTPUT_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataOutputRemoved"
                    defaults="Technical Asset removed: link removed with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );

        case EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataOutputDatasetLinkRequested"
                    defaults="Requested producing link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_OUTPUT_DATASET_LINK_APPROVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataOutputDatasetLinkApproved"
                    defaults="Approved producing link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_OUTPUT_DATASET_LINK_DENIED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataOutputDatasetLinkDenied"
                    defaults="Denied producing link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_OUTPUT_DATASET_LINK_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataOutputDatasetLinkRemoved"
                    defaults="Removed producing link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );

        case EventType.DATA_PRODUCT_CREATED:
            return <Trans t={t} i18nKey="EventDataProductCreated" defaults="Data Product created" />;
        case EventType.DATA_PRODUCT_UPDATED:
            return <Trans t={t} i18nKey="EventDataProductUpdated" defaults="Data Product updated" />;
        case EventType.DATA_PRODUCT_REMOVED:
            return <Trans t={t} i18nKey="EventDataProductRemoved" defaults="Data Product removed" />;
        case EventType.DATA_PRODUCT_SETTING_UPDATED:
            return <Trans t={t} i18nKey="EventDataProductSettingUpdated" defaults="Data Product setting updated" />;
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductRoleAssignmentCreated"
                    defaults="Added <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductRoleAssignmentUpdated"
                    defaults="Updated role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductRoleAssignmentRemoved"
                    defaults="Removed <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductRoleAssignmentRequested"
                    defaults="Requested role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductRoleAssignmentApproved"
                    defaults="Approved role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductRoleAssignmentDenied"
                    defaults="Denied role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );

        case EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductDatasetLinkRequested"
                    defaults="Requested consuming link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_DATASET_LINK_APPROVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductDatasetLinkApproved"
                    defaults="Approved consuming link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_DATASET_LINK_DENIED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductDatasetLinkDenied"
                    defaults="Denied consuming link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );
        case EventType.DATA_PRODUCT_DATASET_LINK_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDataProductDatasetLinkRemoved"
                    defaults="Removed consuming link with the <element>{{entity}}</element> {{entity_type}}"
                    values={{ entity, entity_type }}
                    components={{ element }}
                />
            );

        case EventType.DATASET_ROLE_ASSIGNMENT_CREATED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDatasetRoleAssignmentCreated"
                    defaults="Added <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATASET_ROLE_ASSIGNMENT_UPDATED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDatasetRoleAssignmentUpdated"
                    defaults="Updated role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATASET_ROLE_ASSIGNMENT_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDatasetRoleAssignmentRemoved"
                    defaults="Removed <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATASET_ROLE_ASSIGNMENT_REQUESTED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDatasetRoleAssignmentRequested"
                    defaults="Requested role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATASET_ROLE_ASSIGNMENT_APPROVED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDatasetRoleAssignmentApproved"
                    defaults="Approved role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );
        case EventType.DATASET_ROLE_ASSIGNMENT_DENIED:
            return (
                <Trans
                    t={t}
                    i18nKey="EventDatasetRoleAssignmentDenied"
                    defaults="Denied role for <element>{{entity}}</element>"
                    values={{ entity }}
                    components={{ element }}
                />
            );

        case EventType.DATASET_CREATED:
            return <Trans t={t} i18nKey="EventDatasetCreated" defaults="Dataset created" />;
        case EventType.DATASET_UPDATED:
            return <Trans t={t} i18nKey="EventDatasetUpdated" defaults="Dataset updated" />;
        case EventType.DATASET_REMOVED:
            return <Trans t={t} i18nKey="EventDatasetRemoved" defaults="Dataset removed" />;
        case EventType.DATASET_SETTING_UPDATED:
            return <Trans t={t} i18nKey="EventDatasetSettingUpdated" defaults="Dataset setting updated" />;
        default:
            throw new Error(`Unsupported event type ${event_type}`);
    }
}

export function getNotificationDisplayName(
    t: TFunction,
    event_type: EventType,
    subject_entity_reference: EventEntityType,
    subject_entity: string,
    target_entity_reference: EventEntityType | null | undefined,
    target_entity: string,
    subject: ReactElement,
    target: ReactElement,
): ReactNode | null {
    const subject_entity_type = getTypeDisplayName(t, subject_entity_reference);
    const target_entity_type = getTypeDisplayName(t, target_entity_reference);

    switch (event_type) {
        case EventType.DATA_OUTPUT_CREATED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataOutputCreated"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} has been created for the <target>{{target_entity}}</target> {{target_entity_type}}"
                    values={{ subject_entity, subject_entity_type, target_entity, target_entity_type }}
                    components={{ subject, target }}
                />
            );
        case EventType.DATA_OUTPUT_UPDATED:
            return;
        case EventType.DATA_OUTPUT_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataOutputRemoved"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} has been removed from the <target>{{target_entity}}</target> {{target_entity_type}}"
                    values={{ subject_entity, subject_entity_type, target_entity, target_entity_type }}
                    components={{ subject, target }}
                />
            );

        case EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED:
        case EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED:
            return;
        case EventType.DATA_OUTPUT_DATASET_LINK_APPROVED:
        case EventType.DATA_PRODUCT_DATASET_LINK_APPROVED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataOutputLinkApproved"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} is now linked to the <target>{{target_entity}}</target> {{target_entity_type}}"
                    values={{ subject_entity, subject_entity_type, target_entity, target_entity_type }}
                    components={{ subject, target }}
                />
            );
        case EventType.DATA_OUTPUT_DATASET_LINK_DENIED:
        case EventType.DATA_PRODUCT_DATASET_LINK_DENIED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataOutputLinkDenied"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} link denied for the <target>{{target_entity}}</target> {{target_entity_type}}"
                    values={{ subject_entity, subject_entity_type, target_entity, target_entity_type }}
                    components={{ subject, target }}
                />
            );
        case EventType.DATA_OUTPUT_DATASET_LINK_REMOVED:
        case EventType.DATA_PRODUCT_DATASET_LINK_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataOutputLinkRemoved"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} has been unlinked from the <target>{{target_entity}}</target> {{target_entity_type}}"
                    values={{ subject_entity, subject_entity_type, target_entity, target_entity_type }}
                    components={{ subject, target }}
                />
            );

        case EventType.DATA_PRODUCT_CREATED:
        case EventType.DATASET_CREATED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataProductCreated"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} has been created"
                    values={{ subject_entity, subject_entity_type }}
                    components={{ subject }}
                />
            );
        case EventType.DATA_PRODUCT_UPDATED:
        case EventType.DATASET_UPDATED:
        case EventType.DATA_PRODUCT_SETTING_UPDATED:
        case EventType.DATASET_SETTING_UPDATED:
            return;
        case EventType.DATA_PRODUCT_REMOVED:
        case EventType.DATASET_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataProductRemoved"
                    defaults="<subject>{{subject_entity}}</subject> {{subject_entity_type}} has been removed"
                    values={{ subject_entity, subject_entity_type }}
                    components={{ subject }}
                />
            );

        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED:
        case EventType.DATASET_ROLE_ASSIGNMENT_CREATED:
            return;
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED:
        case EventType.DATASET_ROLE_ASSIGNMENT_UPDATED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataProductRoleAssignmentUpdated"
                    defaults="role updated for <target>{{target_entity}}</target> in <subject>{{subject_entity}}</subject> {{subject_entity_type}}"
                    values={{ target_entity, subject_entity, subject_entity_type }}
                    components={{ target, subject }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED:
        case EventType.DATASET_ROLE_ASSIGNMENT_REMOVED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataProductRoleAssignmentRemoved"
                    defaults="role removed for <target>{{target_entity}}</target> in <subject>{{subject_entity}}</subject> {{subject_entity_type}}"
                    values={{ target_entity, subject_entity, subject_entity_type }}
                    components={{ target, subject }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED:
        case EventType.DATASET_ROLE_ASSIGNMENT_REQUESTED:
            return;
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED:
        case EventType.DATASET_ROLE_ASSIGNMENT_APPROVED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataProductRoleAssignmentApproved"
                    defaults="role approved for <target>{{target_entity}}</target> in <subject>{{subject_entity}}</subject> {{subject_entity_type}}"
                    values={{ target_entity, subject_entity, subject_entity_type }}
                    components={{ target, subject }}
                />
            );
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED:
        case EventType.DATASET_ROLE_ASSIGNMENT_DENIED:
            return (
                <Trans
                    t={t}
                    i18nKey="NotificationDataProductRoleAssignmentDenied"
                    defaults="role denied for <target>{{target_entity}}</target> in <subject>{{subject_entity}}</subject> {{subject_entity_type}}"
                    values={{ target_entity, subject_entity, subject_entity_type }}
                    components={{ target, subject }}
                />
            );
        default:
            throw new Error(`Unsupported event type ${event_type}`);
    }
}

// Identical in function to `getEventTypeDisplayName` above, but returns plain text
// instead of a React component. Useful for filtering.
export function getEventTypeDisplayText(
    t: TFunction,
    event_type: EventType,
    entity: string,
    entity_reference?: EventEntityType | null,
): string {
    const result = getEventTypeDisplayTranslation(t, event_type, entity, entity_reference);

    // Strip html tags
    return result.replace(/<[^>]*>/g, '');
}

function getEventTypeDisplayTranslation(
    t: TFunction,
    event_type: EventType,
    entity: string,
    entity_reference: EventEntityType | null | undefined,
): string {
    const entity_type = getTypeDisplayName(t, entity_reference);

    switch (event_type) {
        case EventType.DATA_OUTPUT_CREATED:
            return t('EventDataOutputCreated', { entity, entity_type });
        case EventType.DATA_OUTPUT_UPDATED:
            return t('EventDataOutputUpdated', { entity, entity_type });
        case EventType.DATA_OUTPUT_REMOVED:
            return t('EventDataOutputRemoved', { entity, entity_type });

        case EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED:
            return t('EventDataOutputDatasetLinkRequested', { entity, entity_type });
        case EventType.DATA_OUTPUT_DATASET_LINK_APPROVED:
            return t('EventDataOutputDatasetLinkApproved', { entity, entity_type });
        case EventType.DATA_OUTPUT_DATASET_LINK_DENIED:
            return t('EventDataOutputDatasetLinkDenied', { entity, entity_type });
        case EventType.DATA_OUTPUT_DATASET_LINK_REMOVED:
            return t('EventDataOutputDatasetLinkRemoved', { entity, entity_type });

        case EventType.DATA_PRODUCT_CREATED:
            return t('EventDataProductCreated', { entity, entity_type });
        case EventType.DATA_PRODUCT_UPDATED:
            return t('EventDataProductUpdated', { entity, entity_type });
        case EventType.DATA_PRODUCT_REMOVED:
            return t('EventDataProductRemoved', { entity, entity_type });
        case EventType.DATA_PRODUCT_SETTING_UPDATED:
            return t('EventDataProductSettingUpdated', { entity, entity_type });

        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED:
            return t('EventDataProductRoleAssignmentCreated', { entity });
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED:
            return t('EventDataProductRoleAssignmentUpdated', { entity });
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED:
            return t('EventDataProductRoleAssignmentRemoved', { entity });
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED:
            return t('EventDataProductRoleAssignmentRequested', { entity });
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED:
            return t('EventDataProductRoleAssignmentApproved', { entity });
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED:
            return t('EventDataProductRoleAssignmentDenied', { entity });

        case EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED:
            return t('EventDataProductDatasetLinkRequested', { entity, entity_type });
        case EventType.DATA_PRODUCT_DATASET_LINK_APPROVED:
            return t('EventDataProductDatasetLinkApproved', { entity, entity_type });
        case EventType.DATA_PRODUCT_DATASET_LINK_DENIED:
            return t('EventDataProductDatasetLinkDenied', { entity, entity_type });
        case EventType.DATA_PRODUCT_DATASET_LINK_REMOVED:
            return t('EventDataProductDatasetLinkRemoved', { entity, entity_type });

        case EventType.DATASET_ROLE_ASSIGNMENT_CREATED:
            return t('EventDatasetRoleAssignmentCreated', { entity });
        case EventType.DATASET_ROLE_ASSIGNMENT_UPDATED:
            return t('EventDatasetRoleAssignmentUpdated', { entity });
        case EventType.DATASET_ROLE_ASSIGNMENT_REMOVED:
            return t('EventDatasetRoleAssignmentRemoved', { entity });
        case EventType.DATASET_ROLE_ASSIGNMENT_REQUESTED:
            return t('EventDatasetRoleAssignmentRequested', { entity });
        case EventType.DATASET_ROLE_ASSIGNMENT_APPROVED:
            return t('EventDatasetRoleAssignmentApproved', { entity });
        case EventType.DATASET_ROLE_ASSIGNMENT_DENIED:
            return t('EventDatasetRoleAssignmentDenied', { entity });

        case EventType.DATASET_CREATED:
            return t('EventDatasetCreated', { entity, entity_type });
        case EventType.DATASET_UPDATED:
            return t('EventDatasetUpdated', { entity, entity_type });
        case EventType.DATASET_REMOVED:
            return t('EventDatasetRemoved', { entity, entity_type });
        case EventType.DATASET_SETTING_UPDATED:
            return t('EventDatasetSettingUpdated', { entity, entity_type });
        default:
            throw new Error(`Unsupported event type ${event_type}`);
    }
}
