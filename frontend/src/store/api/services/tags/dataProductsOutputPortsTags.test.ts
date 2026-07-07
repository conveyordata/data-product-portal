import { describe, expect, it } from 'vitest';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';
import { dataProductOutputPortTags } from '@/store/api/services/tags/dataProductsOutputPortsTags.ts';

describe('dataProductOutputPortTags invalidation', () => {
    const args = { dataProductId: 'dp1', id: 'op1' };

    it('removeOutputPort does not invalidate the deleted port per-id tag (regression guard for 404)', () => {
        const tags = dataProductOutputPortTags.removeOutputPort.invalidatesTags(undefined, undefined, args);

        expect(tags).not.toContainEqual({ type: TagTypes.OutputPort, id: 'op1' });
    });

    it('removeOutputPort still invalidates the list and parent tags so the deletion is reflected', () => {
        const tags = dataProductOutputPortTags.removeOutputPort.invalidatesTags(undefined, undefined, args);

        expect(tags).toContainEqual({ type: TagTypes.OutputPort, id: STATIC_TAG_ID.LIST });
        expect(tags).toContainEqual({ type: TagTypes.DataProductOutputPorts, id: 'dp1' });
    });

    it('updateOutputPort still invalidates the per-id tag so the entity refetches', () => {
        const tags = dataProductOutputPortTags.updateOutputPort.invalidatesTags(undefined, undefined, args);

        expect(tags).toContainEqual({ type: TagTypes.OutputPort, id: 'op1' });
    });
});
