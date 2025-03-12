import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';

export function getDynamicRoutePath(path: string, param: DynamicPathParams, value: string) {
    return path.replace(`:${param}`, value);
}

export function isDataProductEditPage(path: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataProductEdit, DynamicPathParams.DataProductId, dataProductId) === path
    );
}

export function isDataOutputEditPage(path: string, dataOutputId: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataOutputEdit, DynamicPathParams.DataOutputId, dataOutputId).replace(
            ':' + DynamicPathParams.DataProductId,
            dataProductId,
        ) === path
    );
}

export function isEnvironmentConfigsPage(path: string, environmentId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.EnvironmentConfigs, DynamicPathParams.EnvironmentId, environmentId) ===
        path
    );
}

export function isEnvironmentConfigCreatePage(path: string, environmentId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.EnvironmentConfigNew, DynamicPathParams.EnvironmentId, environmentId) ===
        path
    );
}

export function isEnvConfigPage(path: string, envConfigId: string) {
    return getDynamicRoutePath(ApplicationPaths.EnvironmentConfig, DynamicPathParams.EnvConfigId, envConfigId) === path;
}
