import type { TFunction } from 'i18next';

import type { UiElementMetadataResponse } from '@/store/api/services/generated/pluginsApi';
import { getIcon } from './icon-loader';

export function getDataOutputIcon(configuration_type: string | undefined, plugins?: UiElementMetadataResponse[]) {
    if (!configuration_type || !plugins) {
        return undefined;
    }

    const plugin = plugins.find((p) => p.plugin === configuration_type);
    if (!plugin) {
        return undefined;
    }

    // Replace logo with border-icon
    const borderIcon = plugin.icon_name.replace('logo', 'border-icon');
    return getIcon(borderIcon);
}

export function getDataOutputType(
    configuration_type: string | undefined,
    plugins: UiElementMetadataResponse[] | undefined,
    t: TFunction,
) {
    if (!configuration_type || !plugins) {
        return undefined;
    }

    const plugin = plugins.find((p) => p.plugin === configuration_type);
    if (!plugin) {
        return undefined;
    }

    return t(plugin.display_name);
}
