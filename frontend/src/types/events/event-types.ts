export const EventType = {
    DATA_OUTPUT_CREATED: 'data_output_created',
    DATA_OUTPUT_UPDATED: 'data_output_updated',
    DATA_OUTPUT_REMOVED: 'data_output_removed',

    DATA_OUTPUT_DATASET_LINK_REQUESTED: 'data_output_dataset_link_requested',
    DATA_OUTPUT_DATASET_LINK_APPROVED: 'data_output_dataset_link_approved',
    DATA_OUTPUT_DATASET_LINK_DENIED: 'data_output_dataset_link_denied',
    DATA_OUTPUT_DATASET_LINK_REMOVED: 'data_output_dataset_link_removed',

    DATA_PRODUCT_CREATED: 'data_product_created',
    DATA_PRODUCT_UPDATED: 'data_product_updated',
    DATA_PRODUCT_REMOVED: 'data_product_removed',
    DATA_PRODUCT_MEMBERSHIP_CREATED: 'data_product_membership_created',
    DATA_PRODUCT_MEMBERSHIP_UPDATED: 'data_product_membership_updated',
    DATA_PRODUCT_MEMBERSHIP_REMOVED: 'data_product_membership_removed',
    DATA_PRODUCT_MEMBERSHIP_REQUESTED: 'data_product_membership_requested',
    DATA_PRODUCT_MEMBERSHIP_APPROVED: 'data_product_membership_approved',
    DATA_PRODUCT_MEMBERSHIP_DENIED: 'data_product_membership_denied',

    DATA_PRODUCT_DATASET_LINK_REQUESTED: 'data_product_dataset_link_requested',
    DATA_PRODUCT_DATASET_LINK_APPROVED: 'data_product_dataset_link_approved',
    DATA_PRODUCT_DATASET_LINK_DENIED: 'data_product_dataset_link_denied',
    DATA_PRODUCT_DATASET_LINK_REMOVED: 'data_product_dataset_link_removed',

    DATASET_CREATED: 'dataset_created',
    DATASET_UPDATED: 'dataset_updated',
    DATASET_REMOVED: 'dataset_removed',
    DATASET_USER_ADDED: 'dataset_user_added',
    DATASET_USER_REMOVED: 'dataset_user_removed',
} as const;

export type EventType = (typeof EventType)[keyof typeof EventType];
