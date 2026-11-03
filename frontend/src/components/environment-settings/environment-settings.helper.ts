import {
    type EnvironmentUiMetadata,
    UIElementType,
    type UiElementMetadata,
} from '@/store/api/services/generated/pluginsApi';

export type EnvironmentValues = Record<string, Record<string, unknown>>;

export type EnvironmentSettingsError = {
    environment_id: string;
    field?: string | null;
    message: string;
};

export type EnvironmentChange = {
    field: string;
    label: string;
    from: string;
    to: string;
};

export const displayValue = (value: unknown) => (value === undefined || value === null ? '' : String(value));

export const isSameValue = (a: unknown, b: unknown) => displayValue(a) === displayValue(b);

const renderPlaceholders = (value: unknown, shared: Record<string, unknown>) =>
    typeof value === 'string'
        ? value.replace(/\{(\w+)(?::\.(\d+))?\}/g, (_, name: string, length?: string) =>
              displayValue(shared[name]).slice(0, length ? Number(length) : undefined),
          )
        : value;

const initialValue = (field: UiElementMetadata, shared: Record<string, unknown>): unknown => {
    switch (field.type) {
        case UIElementType.Select:
            return field.select?.initial_value ?? undefined;
        case UIElementType.Radio:
            return field.radio?.initial_value ?? undefined;
        case UIElementType.Checkbox:
            return field.checkbox?.initial_value ?? false;
        default:
            return renderPlaceholders(field.string?.initial_value ?? '', shared);
    }
};

export const buildDefaultValues = (
    metadata: EnvironmentUiMetadata[],
    shared: Record<string, unknown> = {},
): EnvironmentValues =>
    Object.fromEntries(
        metadata.map(({ environment_id, ui_metadata }) => [
            environment_id,
            Object.fromEntries(ui_metadata.map((field) => [field.name, initialValue(field, shared)])),
        ]),
    );

export const followDefaults = (
    previous: EnvironmentValues,
    next: EnvironmentValues,
    current: EnvironmentValues,
): EnvironmentValues =>
    Object.fromEntries(
        Object.entries(next).map(([environmentId, fields]) => [
            environmentId,
            Object.fromEntries(
                Object.entries(fields).map(([name, value]) => [
                    name,
                    isSameValue(current[environmentId]?.[name], previous[environmentId]?.[name])
                        ? value
                        : current[environmentId]?.[name],
                ]),
            ),
        ]),
    );

export const optionLabel = (field: UiElementMetadata, value: unknown) => {
    const options = field.select?.options ?? field.radio?.options ?? [];
    return options.find((option) => isSameValue(option.value, value))?.label ?? displayValue(value);
};

export const computeChanges = (
    metadata: EnvironmentUiMetadata[],
    baseline: EnvironmentValues,
    current: EnvironmentValues,
): Record<string, EnvironmentChange[]> =>
    Object.fromEntries(
        metadata.map(({ environment_id, ui_metadata }) => [
            environment_id,
            ui_metadata
                .filter(
                    (field) =>
                        !isSameValue(baseline[environment_id]?.[field.name], current[environment_id]?.[field.name]),
                )
                .map((field) => ({
                    field: field.name,
                    label: field.label,
                    from: optionLabel(field, baseline[environment_id]?.[field.name]),
                    to: optionLabel(field, current[environment_id]?.[field.name]),
                })),
        ]),
    );

export const getEnvironmentSettingsErrors = (error: unknown): EnvironmentSettingsError[] => {
    if (!error || typeof error !== 'object') {
        return [];
    }
    const { detail, data } = error as { detail?: unknown; data?: { detail?: unknown } };
    const errors = data?.detail ?? detail;
    return Array.isArray(errors) ? errors.filter((item) => item && typeof item.environment_id === 'string') : [];
};
