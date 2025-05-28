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
    DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED: 'data_product_role_assignment_created',
    DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED: 'data_product_role_assignment_updated',
    DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED: 'data_product_role_assignment_removed',
    DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED: 'data_product_role_assignment_requested',
    DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED: 'data_product_role_assignment_approved',
    DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED: 'data_product_role_assignment_denied',

    DATA_PRODUCT_DATASET_LINK_REQUESTED: 'data_product_dataset_link_requested',
    DATA_PRODUCT_DATASET_LINK_APPROVED: 'data_product_dataset_link_approved',
    DATA_PRODUCT_DATASET_LINK_DENIED: 'data_product_dataset_link_denied',
    DATA_PRODUCT_DATASET_LINK_REMOVED: 'data_product_dataset_link_removed',

    DATASET_CREATED: 'dataset_created',
    DATASET_UPDATED: 'dataset_updated',
    DATASET_REMOVED: 'dataset_removed',
    DATASET_ROLE_ASSIGNMENT_CREATED: 'dataset_role_assignment_created',
    DATASET_ROLE_ASSIGNMENT_UPDATED: 'dataset_role_assignment_updated',
    DATASET_ROLE_ASSIGNMENT_REMOVED: 'dataset_role_assignment_removed',
    DATASET_ROLE_ASSIGNMENT_REQUESTED: 'dataset_role_assignment_requested',
    DATASET_ROLE_ASSIGNMENT_APPROVED: 'dataset_role_assignment_approved',
    DATASET_ROLE_ASSIGNMENT_DENIED: 'dataset_role_assignment_denied',
} as const;

export type EventType = (typeof EventType)[keyof typeof EventType];
