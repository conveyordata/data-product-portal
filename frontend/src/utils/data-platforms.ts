import { generateDataPlatformsFromYaml, useDataPlatformsFromRegistry } from '@/utils/dynamic-data-platforms';

// Dynamic version using YAML registry
export const getDataPlatformsFromYaml = generateDataPlatformsFromYaml;
export const useDataPlatforms = useDataPlatformsFromRegistry;
