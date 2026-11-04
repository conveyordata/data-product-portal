import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDebouncedCallback } from 'use-debounce';
import {
    type GetTechnicalAssetResponse,
    useUpdateTechnicalAssetEnvironmentConfigurationMutation,
    useValidateTechnicalAssetEnvironmentConfigurationMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { dispatchMessage } from '@/utils/feedback';
import {
    computeChanges,
    type EnvironmentSettingsError,
    type EnvironmentValues,
    getEnvironmentSettingsErrors,
} from './environment-settings.helper';

export type EnvironmentSettingsAsset = Pick<
    GetTechnicalAssetResponse,
    'id' | 'configuration' | 'environments' | 'environment_values'
>;

const NO_VALUES: EnvironmentValues = {};
const VALIDATE_DEBOUNCE = 500;

export function useEnvironmentSettings(dataProductId: string, technicalAsset: EnvironmentSettingsAsset | undefined) {
    const { t } = useTranslation();
    const { data: { plugins } = {} } = useGetPluginsQuery();
    const [update, { isLoading: isSaving }] = useUpdateTechnicalAssetEnvironmentConfigurationMutation();
    const stored: EnvironmentValues = technicalAsset?.environment_values ?? NO_VALUES;
    const [values, setValues] = useState<EnvironmentValues>(stored);
    const [validate, { isLoading: isValidating }] = useValidateTechnicalAssetEnvironmentConfigurationMutation();
    const [errors, setErrors] = useState<EnvironmentSettingsError[]>([]);
    const latestCheck = useRef(0);

    useEffect(() => setValues(stored), [stored]);

    const environments = useMemo(() => technicalAsset?.environments.map((e) => e.environment) ?? [], [technicalAsset]);
    const metadata = useMemo(() => {
        const ids = new Set(environments.map((e) => e.id));
        return (
            plugins
                ?.find((plugin) => plugin.plugin === technicalAsset?.configuration.name)
                ?.environment_ui_metadata?.filter((item) => ids.has(item.environment_id)) ?? []
        );
    }, [plugins, technicalAsset, environments]);

    const changes = useMemo(() => computeChanges(metadata, stored, values), [metadata, stored, values]);
    const changedEnvironments = environments.filter((e) => changes[e.id]?.length);

    const runCheck = async (submitted: EnvironmentValues): Promise<boolean> => {
        if (!technicalAsset) return false;
        const id = ++latestCheck.current;
        try {
            await validate({
                dataProductId,
                id: technicalAsset.id,
                technicalAssetEnvironmentConfigurationUpdate: { environment_values: submitted },
            }).unwrap();
            if (id === latestCheck.current) setErrors([]);
            return true;
        } catch (error) {
            const cellErrors = getEnvironmentSettingsErrors(error);
            if (id === latestCheck.current) setErrors(cellErrors);
            return cellErrors.length === 0;
        }
    };

    const check = useDebouncedCallback(runCheck, VALIDATE_DEBOUNCE);

    const validateNow = (): Promise<boolean> => {
        check.cancel();
        return runCheck(values);
    };

    const hasChanges = changedEnvironments.length > 0;
    useEffect(() => {
        if (hasChanges) {
            check(values);
        } else {
            check.cancel();
            latestCheck.current++;
            setErrors([]);
        }
    }, [values, hasChanges, check]);

    const reset = () => {
        setValues(stored);
        setErrors([]);
    };

    const save = async (): Promise<boolean> => {
        if (!technicalAsset) return false;
        check.cancel();
        latestCheck.current++;
        try {
            await update({
                dataProductId,
                id: technicalAsset.id,
                technicalAssetEnvironmentConfigurationUpdate: { environment_values: values },
            }).unwrap();
            setErrors([]);
            return true;
        } catch (error) {
            const cellErrors = getEnvironmentSettingsErrors(error);
            setErrors(cellErrors);
            if (cellErrors.length === 0) {
                dispatchMessage({ content: t('Failed to save Environment Settings'), type: 'error' });
            }
            return false;
        }
    };

    return {
        environments,
        metadata,
        stored,
        values,
        setValues,
        changes,
        changedEnvironments,
        errors,
        reset,
        save,
        isSaving,
        validateNow,
        isValidating,
    };
}
