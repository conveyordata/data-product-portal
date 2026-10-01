import { render } from '@testing-library/react';
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

function renderIcon(Icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>) {
    if (!Icon) {
        throw new Error('expected an icon component');
    }
    return render(<Icon />).container.firstElementChild;
}

describe('getTechnicalAssetIcon', () => {
    it('uses the icon a plugin bundles in its own package', () => {
        const icon = renderIcon(getTechnicalAssetIcon('SomePlugin', [plugin({ icon_data_uri: DATA_URI })]));

        // An <svg>, so the `svg { width; height }` rule every caller relies on sizes it.
        expect(icon?.tagName.toLowerCase()).toBe('svg');
        expect(icon?.querySelector('image')?.getAttribute('href')).toBe(DATA_URI);
    });

    it('falls back to the bundled frontend asset when the plugin ships no icon', () => {
        const icon = renderIcon(getTechnicalAssetIcon('SomePlugin', [plugin()]));

        expect(icon?.querySelector('image')).toBeNull();
    });

    it('returns nothing for an unknown plugin', () => {
        expect(getTechnicalAssetIcon('NoSuchPlugin', [plugin()])).toBeUndefined();
    });
});

describe('getPlatformTileIcon', () => {
    it('uses the tile icon a plugin bundles in its own package', () => {
        const icon = renderIcon(getPlatformTileIcon(tile({ icon_data_uri: DATA_URI })));

        expect(icon?.tagName.toLowerCase()).toBe('svg');
        expect(icon?.querySelector('image')?.getAttribute('href')).toBe(DATA_URI);
    });

    it('falls back to the bundled frontend asset', () => {
        const icon = renderIcon(getPlatformTileIcon(tile()));

        expect(icon?.querySelector('image')).toBeNull();
    });

    it('returns the same component for the same icon, so React does not remount it', () => {
        expect(getPlatformTileIcon(tile({ icon_data_uri: DATA_URI }))).toBe(
            getPlatformTileIcon(tile({ icon_data_uri: DATA_URI })),
        );
    });
});
