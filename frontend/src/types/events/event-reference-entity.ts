export const EventReferenceEntity = {
    Dataset: 'dataset',
    DataProduct: 'data_product',
    DataOutput: 'data_output',
    User: 'user',
} as const;

export type EventReferenceEntity = (typeof EventReferenceEntity)[keyof typeof EventReferenceEntity];
