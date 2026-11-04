import { describe, expect, it } from 'vitest';
import { dataProductTechnicalAssetsTags } from '@/store/api/services/tags/dataProductsTechicalAssetsTags.ts';

describe('dataProductTechnicalAssetsTags', () => {
    it('suppresses the generic toast when creating a technical asset', () => {
        expect(dataProductTechnicalAssetsTags.createTechnicalAsset.extraOptions).toEqual({
            suppressErrorToast: true,
        });
    });

    it('suppresses the generic toast when validating Environment Settings', () => {
        expect(dataProductTechnicalAssetsTags.validateTechnicalAssetEnvironmentConfiguration.extraOptions).toEqual({
            suppressErrorToast: true,
        });
    });
});
