import { DataOutputDatasetContract } from '../data-output-dataset';
import { DataProductDatasetContract } from '../data-product-dataset';
import { DataProductMembershipContract } from '../data-product-membership';
import { UserContract } from '../users';

export enum NotificationTypes {
    DataProductDataset = 'DataProductDataset',
    DataOutputDataset = 'DataOutputDataset',
    DataProductMembership = 'DataProductMembership',
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

export type Notification =
    | DataProductDatasetNotification
    | DataOutputDatasetNotification
    | DataProductMembershipNotification;

export interface DataProductDatasetNotification {
    configuration_type: NotificationTypes.DataProductDataset;
    data_product_dataset_id: string;
    data_product_dataset: DataProductDatasetContract;
}

export interface DataOutputDatasetNotification {
    configuration_type: NotificationTypes.DataOutputDataset;
    data_output_dataset_id: string;
    data_output_dataset: DataOutputDatasetContract;
}

export interface DataProductMembershipNotification {
    configuration_type: NotificationTypes.DataProductMembership;
    data_product_membership_id: string;
    data_product_membership: DataProductMembershipContract;
}
