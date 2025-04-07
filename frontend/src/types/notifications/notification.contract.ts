import { DataOutputDatasetContract, DataOutputDatasetLinkRequest } from '../data-output-dataset';
import { DataProductDatasetContract, DataProductDatasetLinkRequest } from '../data-product-dataset';
import { DataProductMembershipContract } from '../data-product-membership';
import { UserContract } from '../users';

export enum NotificationTypes {
    DataProductDatasetNotification = 'DataProductDatasetNotification',
    DataOutputDatasetNotification = 'DataOutputDatasetNotification',
    DataProductMembershipNotification = 'DataProductMembershipNotification',
}

export interface NotificationModel {
    id: string;
    notification_id: string;
    notification: Notification;
    user_id: string;
    user: UserContract;
    last_seen: string | null;
    last_interaction: string | null;
}

export type NotificationObject = DataProductMembershipContract | DataProductDatasetContract | DataOutputDatasetContract;

export type Notification =
    | DataProductDatasetNotification
    | DataOutputDatasetNotification
    | DataProductMembershipNotification;

export interface DataProductDatasetNotification {
    configuration_type: NotificationTypes.DataProductDatasetNotification;
    id: string;
    reference_id: string;
    reference: DataProductDatasetContract;
}

export interface DataOutputDatasetNotification {
    configuration_type: NotificationTypes.DataOutputDatasetNotification;
    id: string;
    reference_id: string;
    reference: DataOutputDatasetContract;
}

export interface DataProductMembershipNotification {
    configuration_type: NotificationTypes.DataProductMembershipNotification;
    id: string;
    reference_id: string;
    reference: DataProductMembershipContract;
}

export type ActionResolveRequest =
    | { type: NotificationTypes.DataOutputDatasetNotification; request: DataOutputDatasetLinkRequest }
    | { type: NotificationTypes.DataProductDatasetNotification; request: DataProductDatasetLinkRequest }
    | { type: NotificationTypes.DataProductMembershipNotification; request: string };
