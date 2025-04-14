import { DataOutputDatasetContract, DataOutputDatasetLinkStatus } from '../data-output-dataset';
import { DataProductDatasetContract, DataProductDatasetLinkStatus } from '../data-product-dataset';
import { DataProductMembershipContract, DataProductMembershipStatus } from '../data-product-membership';
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
}

export type NotificationObject = DataProductMembershipContract | DataProductDatasetContract | DataOutputDatasetContract;

export type Notification =
    | DataProductDatasetNotification
    | DataOutputDatasetNotification
    | DataProductMembershipNotification;

export interface DataProductDatasetNotification {
    notification_type: NotificationTypes.DataProductDatasetNotification;
    notification_origin: DataProductDatasetLinkStatus;
    id: string;
    data_product_dataset_id: string;
    data_product_dataset: DataProductDatasetContract;
}

export interface DataOutputDatasetNotification {
    notification_type: NotificationTypes.DataOutputDatasetNotification;
    notification_origin: DataOutputDatasetLinkStatus;
    id: string;
    data_output_dataset_id: string;
    data_output_dataset: DataOutputDatasetContract;
}

export interface DataProductMembershipNotification {
    notification_type: NotificationTypes.DataProductMembershipNotification;
    notification_origin: DataProductMembershipStatus;
    id: string;
    data_product_membership_id: string;
    data_product_membership: DataProductMembershipContract;
}
