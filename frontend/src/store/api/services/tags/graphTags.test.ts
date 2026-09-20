import { describe, expect, it } from 'vitest';
import type { CreateOutputPortApiArg } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { dataProductsOutputPortsInputPortsTags } from '@/store/api/services/tags/dataProductsOutputPortsInputPortsTags.ts';
import { dataProductOutputPortTags } from '@/store/api/services/tags/dataProductsOutputPortsTags.ts';
import { dataProductTechnicalAssetsTags } from '@/store/api/services/tags/dataProductsTechicalAssetsTags.ts';
import { dataProductTags } from '@/store/api/services/tags/dataProductTags.ts';
import { explorationTags } from '@/store/api/services/tags/explorationTags.ts';
import { graphTag } from '@/store/api/services/tags/graphTags.ts';

describe('graph cache invalidation', () => {
    it('every graph query provides the shared graph tag', () => {
        expect(dataProductTags.getDataProductGraphData.providesTags).toContainEqual(graphTag);
        expect(dataProductOutputPortTags.getOutputPortGraphData.providesTags).toContainEqual(graphTag);
        expect(dataProductTechnicalAssetsTags.getTechnicalAssetGraphData.providesTags).toContainEqual(graphTag);
    });

    it('approving an output port as input port invalidates the graph', () => {
        const tags = dataProductsOutputPortsInputPortsTags.approveOutputPortAsInputPort.invalidatesTags(
            undefined,
            undefined,
            {
                dataProductId: 'dp1',
                outputPortId: 'op1',
                approveOutputPortAsInputPortRequest: { consuming_data_product_id: 'dp2' },
            },
        );

        expect(tags).toContainEqual(graphTag);
    });

    it('revoking an output port as input port invalidates the graph', () => {
        const tags = dataProductsOutputPortsInputPortsTags.revokeOutputPortAsInputPort.invalidatesTags(
            undefined,
            undefined,
            {
                dataProductId: 'dp1',
                outputPortId: 'op1',
                revokeOutputPortAsInputPortRequest: { consuming_data_product_id: 'dp2' },
            },
        );

        expect(tags).toContainEqual(graphTag);
    });

    it('linking a technical asset to an output port invalidates the graph', () => {
        const tags = dataProductTechnicalAssetsTags.linkOutputPortToTechnicalAsset.invalidatesTags(
            undefined,
            undefined,
            {
                dataProductId: 'dp1',
                outputPortId: 'op1',
                linkTechnicalAssetToOutputPortRequest: { technical_asset_id: 'ta1' },
            },
        );

        expect(tags).toContainEqual(graphTag);
    });

    it('revoking an exploration input port invalidates the graph', () => {
        const tags = explorationTags.revokeInputPortForExploration.invalidatesTags(undefined, undefined, {
            id: 'ex1',
            outputPortId: 'op1',
        });

        expect(tags).toContainEqual(graphTag);
    });

    it('creating an output port invalidates the graph so the new node appears', () => {
        const tags = dataProductOutputPortTags.createOutputPort.invalidatesTags(undefined, undefined, {
            dataProductId: 'dp1',
            createOutputPortRequest: {} as CreateOutputPortApiArg['createOutputPortRequest'],
        });

        expect(tags).toContainEqual(graphTag);
    });
});
