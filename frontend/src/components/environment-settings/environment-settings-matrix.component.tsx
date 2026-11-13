import { Checkbox, Flex, Input, Radio, Select, Table, Tooltip, Typography, theme } from 'antd';
import { useTranslation } from 'react-i18next';
import QuestionTooltip from '@/components/tooltip/question-tooltip';
import type { EnvironmentGetItem } from '@/store/api/services/generated/configurationEnvironmentsApi';
import {
    type EnvironmentUiMetadata,
    type SelectOption,
    UIElementType,
    type UiElementMetadata,
} from '@/store/api/services/generated/pluginsApi';
import {
    displayValue,
    type EnvironmentSettingsError,
    type EnvironmentValues,
    isSameValue,
    optionLabel,
} from './environment-settings.helper';

type Props = {
    environments: EnvironmentGetItem[];
    metadata: EnvironmentUiMetadata[];
    value?: EnvironmentValues;
    onChange?: (value: EnvironmentValues) => void;
    baseline?: EnvironmentValues;
    baselineNote?: (value: string) => string;
    errors?: EnvironmentSettingsError[];
    disabled?: boolean;
};

type Cell = {
    field: UiElementMetadata;
    environmentId: string;
};

const topAligned = () => ({ style: { verticalAlign: 'top' } });

export function EnvironmentSettingsMatrix({
    environments,
    metadata,
    value = {},
    onChange,
    baseline,
    baselineNote,
    errors = [],
    disabled,
}: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const fieldsByEnvironment = new Map(metadata.map((item) => [item.environment_id, item.ui_metadata]));
    const rows = fieldsByEnvironment.get(environments[0]?.id) ?? [];

    const setCell = ({ field, environmentId }: Cell, cellValue: unknown) =>
        onChange?.({ ...value, [environmentId]: { ...value[environmentId], [field.name]: cellValue } });

    const toOption = (option: SelectOption) => ({
        label: option.disabled ? (
            <Tooltip
                title={t(
                    "This option can't be selected in this Environment. Contact your administrator if you expected it to be available.",
                )}
            >
                <div>{option.label}</div>
            </Tooltip>
        ) : (
            option.label
        ),
        value: String(option.value),
        disabled: option.disabled ?? false,
    });

    const renderInput = (cell: Cell) => {
        const { field, environmentId } = cell;
        const current = value[environmentId]?.[field.name];
        const status = errors.some((e) => e.environment_id === environmentId && e.field === field.name)
            ? 'error'
            : baseline && !isSameValue(current, baseline[environmentId]?.[field.name])
              ? 'warning'
              : undefined;
        switch (field.type) {
            case UIElementType.Select:
                return (
                    <Select
                        aria-label={`${field.label} ${environmentId}`}
                        style={{ width: '100%' }}
                        status={status}
                        disabled={disabled}
                        value={current === undefined || current === null ? undefined : String(current)}
                        options={(field.select?.options ?? []).map(toOption)}
                        onChange={(next) => setCell(cell, next)}
                    />
                );
            case UIElementType.Radio:
                return (
                    <Radio.Group
                        disabled={disabled}
                        value={displayValue(current)}
                        options={(field.radio?.options ?? []).map(toOption)}
                        onChange={(event) => setCell(cell, event.target.value)}
                    />
                );
            case UIElementType.Checkbox:
                return (
                    <Checkbox
                        aria-label={`${field.label} ${environmentId}`}
                        disabled={disabled}
                        checked={Boolean(current)}
                        onChange={(event) => setCell(cell, event.target.checked)}
                    />
                );
            default:
                return (
                    <Input
                        aria-label={`${field.label} ${environmentId}`}
                        status={status}
                        disabled={disabled}
                        value={displayValue(current)}
                        onChange={(event) => setCell(cell, event.target.value)}
                    />
                );
        }
    };

    const renderCell = (row: UiElementMetadata, environmentId: string) => {
        const field = fieldsByEnvironment.get(environmentId)?.find((f) => f.name === row.name);
        if (!field) {
            return null;
        }
        const original = baseline?.[environmentId]?.[field.name];
        const changed = baseline && !isSameValue(value[environmentId]?.[field.name], original);
        const cellErrors = errors.filter((e) => e.environment_id === environmentId && e.field === field.name);
        return (
            <Flex vertical gap="small">
                {renderInput({ field, environmentId })}
                {changed && baselineNote && (
                    <Typography.Text type="secondary">{baselineNote(optionLabel(field, original))}</Typography.Text>
                )}
                {cellErrors.map((error) => (
                    <Typography.Text key={error.message} type="danger">
                        {error.message}
                    </Typography.Text>
                ))}
            </Flex>
        );
    };

    return (
        <Table<UiElementMetadata>
            size="small"
            pagination={false}
            scroll={{ x: 'max-content' }}
            rowKey="name"
            dataSource={rows}
            columns={[
                {
                    title: t('Setting'),
                    dataIndex: 'label',
                    width: 160,
                    fixed: 'left' as const,
                    onCell: topAligned,
                    render: (label: string, row: UiElementMetadata) => (
                        <Flex align="center" style={{ minHeight: token.controlHeight }}>
                            {row.tooltip ? <QuestionTooltip title={row.tooltip}>{label}</QuestionTooltip> : label}
                        </Flex>
                    ),
                },
                ...environments.map((environment) => ({
                    key: environment.id,
                    title: (
                        <Flex vertical>
                            <Typography.Text strong>
                                {environment.acronym}{' '}
                                <Typography.Text type="secondary">{environment.name}</Typography.Text>
                            </Typography.Text>
                            {errors
                                .filter((e) => e.environment_id === environment.id && !e.field)
                                .map((error) => (
                                    <Typography.Text key={error.message} type="danger">
                                        {error.message}
                                    </Typography.Text>
                                ))}
                        </Flex>
                    ),
                    width: 140,
                    onCell: topAligned,
                    render: (_: unknown, field: UiElementMetadata) => renderCell(field, environment.id),
                })),
            ]}
        />
    );
}
