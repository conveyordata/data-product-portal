import { DataOutputDatasetContract, DataOutputDatasetLinkRequest } from '../data-output-dataset';
import { DataProductDatasetContract, DataProductDatasetLinkRequest } from '../data-product-dataset';
import { DataProductMembershipContract } from '../data-product-membership';
import { UserContract } from '../users';

export enum NotificationTypes {
    DataProductDatasetNotification = 'DataProductDatasetNotification',
    DataOutputDatasetNotification = 'DataOutputDatasetNotification',
    DataProductMembershipNotification = 'DataProductMembershipNotification',
}

export enum NotificationOrigins {
    Pending = 'pending_approval',
    Approved = 'approved',
    Denied = 'denied',
}

export interface NotificationModel {
    id: string;
    notification_id: string;
    notification: Notification;
    user_id: string;
    user: UserContract;
}

export type Notification =
    | DataProductDatasetNotification
    | DataOutputDatasetNotification
    | DataProductMembershipNotification;

export interface DataProductDatasetNotification {
    notification_type: NotificationTypes.DataProductDatasetNotification;
    notification_origin: NotificationOrigins;
    id: string;
    data_product_dataset_id: string;
    data_product_dataset: DataProductDatasetContract;
}

export interface DataOutputDatasetNotification {
    notification_type: NotificationTypes.DataOutputDatasetNotification;
    notification_origin: NotificationOrigins;
    id: string;
    data_output_dataset_id: string;
    data_output_dataset: DataOutputDatasetContract;
}

export interface DataProductMembershipNotification {
    notification_type: NotificationTypes.DataProductMembershipNotification;
    notification_origin: NotificationOrigins;
    id: string;
    data_product_membership_id: string;
    data_product_membership: DataProductMembershipContract;
}

export type ActionResolveRequest =
    | { type: NotificationTypes.DataOutputDatasetNotification; request: DataOutputDatasetLinkRequest }
    | { type: NotificationTypes.DataProductDatasetNotification; request: DataProductDatasetLinkRequest }
    | { type: NotificationTypes.DataProductMembershipNotification; request: string };
