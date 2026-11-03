import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

export const requestListTags = [
    { type: TagTypes.PendingAction, id: STATIC_TAG_ID.LIST },
    { type: TagTypes.MyRequests, id: STATIC_TAG_ID.LIST },
];
