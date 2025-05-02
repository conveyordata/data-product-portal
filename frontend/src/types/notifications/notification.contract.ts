import { DataOutputDatasetContract } from '../data-output-dataset';
import { DataProductDatasetContract } from '../data-product-dataset';
import { DataProductMembershipContract } from '../data-product-membership';
import { DecisionStatus } from '../roles';
import { UserContract } from '../users';

export enum NotificationTypes {
    DataProductDatasetNotification = 'DataProductDatasetNotification',
    DataOutputDatasetNotification = 'DataOutputDatasetNotification',
    DataProductMembershipNotification = 'DataProductMembershipNotification',
}

export interface BaseNotification {
    notification_origin: DecisionStatus;
    id: string;
    user_id: string;
    user: UserContract;
}

export type Notification =
    | DataProductDatasetNotification
    | DataOutputDatasetNotification
    | DataProductMembershipNotification;

export interface DataProductDatasetNotification extends BaseNotification {
    notification_type: NotificationTypes.DataProductDatasetNotification;
    data_product_dataset_id: string;
    data_product_dataset: DataProductDatasetContract;
    deleted_dataset_identifier: string;
    deleted_data_product_identifier: string;
}

export interface DataOutputDatasetNotification extends BaseNotification {
    notification_type: NotificationTypes.DataOutputDatasetNotification;
    data_output_dataset_id: string;
    data_output_dataset: DataOutputDatasetContract;
    deleted_dataset_identifier: string;
    deleted_data_output_identifier: string;
}

export interface DataProductMembershipNotification extends BaseNotification {
    notification_type: NotificationTypes.DataProductMembershipNotification;
    data_product_membership_id: string;
    data_product_membership: DataProductMembershipContract;
    deleted_data_product_identifier: string;
}
