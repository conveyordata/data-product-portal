import { Notification, NotificationTypes } from '@/types/notifications/notification.contract';

export function getNotificationDataset(notification: Notification): string {
    switch (notification.notification_type) {
        case NotificationTypes.DataProductDatasetNotification: {
            return notification.data_product_dataset
                ? notification.data_product_dataset.dataset.name
                : notification.deleted_dataset_identifier;
        }
        case NotificationTypes.DataOutputDatasetNotification: {
            return notification.data_output_dataset
                ? notification.data_output_dataset.dataset.name
                : notification.deleted_dataset_identifier;
        }
        default:
            return '';
    }
}

export function getNotificationDataProduct(notification: Notification): string {
    switch (notification.notification_type) {
        case NotificationTypes.DataProductDatasetNotification: {
            return notification.data_product_dataset
                ? notification.data_product_dataset.data_product.name
                : notification.deleted_data_product_identifier;
        }
        case NotificationTypes.DataProductMembershipNotification: {
            return notification.data_product_membership
                ? notification.data_product_membership.data_product.name
                : notification.deleted_data_product_identifier;
        }
        default:
            return '';
    }
}

export function getNotificationDataOutput(notification: Notification): string {
    switch (notification.notification_type) {
        case NotificationTypes.DataOutputDatasetNotification: {
            return notification.data_output_dataset
                ? notification.data_output_dataset.data_output.name
                : notification.deleted_data_output_identifier;
        }
        default:
            return '';
    }
}
