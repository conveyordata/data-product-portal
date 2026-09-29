import { describe, expect, it } from 'vitest';
import type { CreateOutputPortRequest } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
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

    it('output port mutations refresh the classification counts', () => {
        const classificationList = { type: TagTypes.OutputPortClassification, id: STATIC_TAG_ID.LIST };

        expect(
            dataProductOutputPortTags.createOutputPort.invalidatesTags(undefined, undefined, {
                dataProductId: 'dp1',
                createOutputPortRequest: {} as CreateOutputPortRequest,
            }),
        ).toContainEqual(classificationList);
        expect(dataProductOutputPortTags.updateOutputPort.invalidatesTags(undefined, undefined, args)).toContainEqual(
            classificationList,
        );
        expect(dataProductOutputPortTags.removeOutputPort.invalidatesTags(undefined, undefined, args)).toContainEqual(
            classificationList,
        );
    });

    it('suppresses the toast for latest data quality summary requests', () => {
        expect(dataProductOutputPortTags.getLatestDataQualitySummaryForOutputPort.extraOptions).toEqual({
            suppressErrorToast: true,
        });
    });
});
