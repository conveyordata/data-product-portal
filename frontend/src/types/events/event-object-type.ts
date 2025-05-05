export const EventObject = {
    Dataset: 'dataset',
    DataProduct: 'data_product',
    DataOutput: 'data_output',
    User: 'user',
} as const;

export type EventObject = (typeof EventObject)[keyof typeof EventObject];
