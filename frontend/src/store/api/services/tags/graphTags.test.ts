import { describe, expect, it } from 'vitest';
import type { ApproveOutputPortAsInputPortRequest } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';
import { dataProductsOutputPortsInputPortsTags } from '@/store/api/services/tags/dataProductsOutputPortsInputPortsTags.ts';
import { dataProductOutputPortTags } from '@/store/api/services/tags/dataProductsOutputPortsTags.ts';

describe('graph tag invalidation', () => {
    it('approving access refreshes every explorer graph', () => {
        const tags = dataProductsOutputPortsInputPortsTags.approveOutputPortAsInputPort.invalidatesTags(
            undefined,
            undefined,
            {
                dataProductId: 'dp1',
                outputPortId: 'op1',
                approveOutputPortAsInputPortRequest: {
                    consuming_data_product_id: 'dp2',
                } as ApproveOutputPortAsInputPortRequest,
            },
        );

        expect(tags).toContainEqual({ type: TagTypes.Graph });
    });

    it('deleting an output port refreshes only the global graph, not its own (regression guard for 404)', () => {
        const tags = dataProductOutputPortTags.removeOutputPort.invalidatesTags(undefined, undefined, {
            dataProductId: 'dp1',
            id: 'op1',
        });

        expect(tags).toContainEqual({ type: TagTypes.Graph, id: STATIC_TAG_ID.LIST });
        expect(tags).not.toContainEqual({ type: TagTypes.Graph });
    });
});
