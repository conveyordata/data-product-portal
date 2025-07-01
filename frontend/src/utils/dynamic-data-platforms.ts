import type { TFunction } from 'i18next';
import yaml from 'js-yaml';
import type { OutputConfig } from '@/types/data-output';
import type { CustomDropdownItemProps } from '@/types/shared';
import { getIcon } from '@/utils/icon.helper';

type PlatformRegistry = Record<string, OutputConfig>;

/**
 * Generates data platforms configuration from YAML registry
 * @param yamlContent - The YAML content as string
 * @param t - Translation function
 * @returns Array of CustomDropdownItemProps for data platforms
 */
export function generateDataPlatformsFromYaml(
    yamlContent: string | undefined,
    t: TFunction,
): CustomDropdownItemProps<string>[] {
    if (yamlContent) {
        try {
            const registry = yaml.load(yamlContent) as PlatformRegistry;

            // First, create a map of all platforms
            const platformMap = new Map<string, CustomDropdownItemProps<string>>();

            // Process each platform in the registry
            for (const [key, config] of Object.entries(registry)) {
                const platformItem: CustomDropdownItemProps<string> = {
                    label: t(key),
                    value: key.toLocaleLowerCase(),
                    icon: getIcon(key.toLocaleLowerCase()),
                    disabled: config.disabled ?? false,
                    hasMenu: config.hasEnvironments ?? false,
                    hasConfig: config.hasConfig ?? false,
                    children: [],
                    marketplace: config.marketplace ?? false,
                };

                platformMap.set(key, platformItem);
            }

            // Second pass: organize parent-child relationships
            const rootPlatforms: CustomDropdownItemProps<string>[] = [];

            for (const [key, config] of Object.entries(registry)) {
                const platformItem = platformMap.get(key);
                if (!platformItem) continue;

                if (config.platform) {
                    // This is a child platform
                    const parentPlatform = platformMap.get(config.platform);
                    if (parentPlatform) {
                        parentPlatform.children?.push(platformItem);
                    } else {
                        // Parent not found, treat as root
                        rootPlatforms.push(platformItem);
                    }
                } else {
                    // This is a root platform
                    rootPlatforms.push(platformItem);
                }
            }

            // Sort platforms (optional - you can customize this logic)
            rootPlatforms.sort((a, b) => a.label.localeCompare(b.label));

            // Sort children within each parent
            rootPlatforms.forEach((platform) => {
                if (platform.children) {
                    platform.children.sort((a, b) => a.label.localeCompare(b.label));
                }
            });

            return rootPlatforms;
        } catch (error) {
            console.error('Error parsing YAML for data platforms:', error);
            // Return fallback static configuration in case of error
            return [];
        }
    } else {
        return [];
    }
}

/**
 * Hook to get data platforms from API
 * This would replace the static getDataPlatforms function
 */
export function useDataPlatformsFromRegistry(yamlContent: string | undefined, t: TFunction) {
    return generateDataPlatformsFromYaml(yamlContent, t);
}
