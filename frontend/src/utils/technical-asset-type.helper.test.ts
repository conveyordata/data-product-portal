import { describe, expect, it } from 'vitest';

import type { PlatformTile, UiElementMetadataResponse } from '@/store/api/services/generated/pluginsApi';
import { getPlatformTileIcon, getTechnicalAssetIcon } from './technical-asset-type.helper';

const DATA_URI = 'data:image/svg+xml;base64,PHN2Zy8+';

function plugin(overrides: Partial<UiElementMetadataResponse> = {}): UiElementMetadataResponse {
    return {
        plugin: 'SomePlugin',
        platform: 'some-platform',
        display_name: 'Some platform',
        icon_name: 'some-logo.svg',
        has_environments: false,
        detailed_name: 'Some platform',
        ui_metadata: [],
        ...overrides,
    } as UiElementMetadataResponse;
}

function tile(overrides: Partial<PlatformTile> = {}): PlatformTile {
    return {
        label: 'Some platform',
        value: 'some-platform',
        icon_name: 'some-logo.svg',
        ...overrides,
    } as PlatformTile;
}

describe('getTechnicalAssetIcon', () => {
    it('uses the icon a plugin bundles in its own package', () => {
        const icon = getTechnicalAssetIcon('SomePlugin', [plugin({ icon_data_uri: DATA_URI })]);

        expect(icon).toBeDefined();
    });

    it('falls back to the bundled frontend asset when the plugin ships no icon', () => {
        const icon = getTechnicalAssetIcon('SomePlugin', [plugin()]);

        expect(icon).toBeDefined();
    });

    it('returns nothing for an unknown plugin', () => {
        expect(getTechnicalAssetIcon('NoSuchPlugin', [plugin()])).toBeUndefined();
    });
});

describe('getPlatformTileIcon', () => {
    it('uses the tile icon a plugin bundles in its own package', () => {
        expect(getPlatformTileIcon(tile({ icon_data_uri: DATA_URI }))).toBeDefined();
    });

    it('falls back to the bundled frontend asset', () => {
        expect(getPlatformTileIcon(tile())).toBeDefined();
    });
});
