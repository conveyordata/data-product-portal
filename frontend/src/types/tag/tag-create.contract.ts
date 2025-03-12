import { TagContract } from '@/types/tag/tag.ts';

export type TagCreateRequest = Pick<TagContract, 'value'>;
export type TagCreateResponse = Pick<TagContract, 'id'>;
