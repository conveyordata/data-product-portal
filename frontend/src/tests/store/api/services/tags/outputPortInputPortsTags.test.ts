import { describe, expect, it } from 'vitest';
import { TagTypes } from '@/store/api/services/tag-types.ts';
import { dataProductsOutputPortsInputPortsTags } from '@/store/api/services/tags/dataProductsOutputPortsInputPortsTags.ts';
import { dataProductTags } from '@/store/api/services/tags/dataProductTags.ts';

describe('OutputPortInputPorts tags', () => {
    it('are keyed by output port id so only that output port refetches', () => {
        const provided = dataProductsOutputPortsInputPortsTags.getInputPortsForOutputPort.providesTags(
            undefined,
            undefined,
            { dataProductId: 'dp1', outputPortId: 'op1' },
        );
        const invalidated = dataProductTags.revokeInputPortForDataProduct.invalidatesTags(undefined, undefined, {
            id: 'dp2',
            outputPortId: 'op1',
        });

        expect(provided).toEqual([{ type: TagTypes.OutputPortInputPorts, id: 'op1' }]);
        expect(invalidated).toContainEqual({ type: TagTypes.OutputPortInputPorts, id: 'op1' });
    });
});
