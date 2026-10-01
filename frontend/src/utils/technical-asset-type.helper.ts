import type { TFunction } from 'i18next';

import type { PlatformTile, UiElementMetadataResponse } from '@/store/api/services/generated/pluginsApi';
import { getIcon, getIconFromDataUri } from './icon-loader';

export function getTechnicalAssetIcon(name: string | undefined, plugins?: UiElementMetadataResponse[]) {
    if (!name || !plugins) {
        return undefined;
    }

    const plugin = plugins.find((p) => p.plugin === name);
    if (!plugin) {
        return undefined;
    }

    if (plugin.icon_data_uri) {
        return getIconFromDataUri(plugin.icon_data_uri);
    }

    return getIcon(plugin.icon_name);
}

export function getTechnicalAssetType(
    name: string | undefined,
    plugins: UiElementMetadataResponse[] | undefined,
    t: TFunction,
) {
    if (!name || !plugins) {
        return undefined;
    }

    const plugin = plugins.find((p) => p.plugin === name);
    if (!plugin) {
        return undefined;
    }

    return t(plugin.display_name);
}

export function getPlatformTileIcon(tile: PlatformTile) {
    return tile.icon_data_uri ? getIconFromDataUri(tile.icon_data_uri) : getIcon(tile.icon_name);
}
