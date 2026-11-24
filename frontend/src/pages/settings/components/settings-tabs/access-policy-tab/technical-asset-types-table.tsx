import { Checkbox, Table, Tooltip } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useTranslation } from 'react-i18next';

export type TechnicalAssetTypeSelection = {
    technical_asset_types: string[];
    default_for_technical_asset_types: string[];
};

type TechnicalAssetTypeOption = {
    label: string;
    value: string;
};

type Props = {
    options: TechnicalAssetTypeOption[];
    typesWithOtherDefault: Set<string>;
    lockedTypes: Map<string, string>;
    loading?: boolean;
    value?: TechnicalAssetTypeSelection;
    onChange?: (value: TechnicalAssetTypeSelection) => void;
};

export function TechnicalAssetTypesTable({
    options,
    typesWithOtherDefault,
    lockedTypes,
    loading,
    value = { technical_asset_types: [], default_for_technical_asset_types: [] },
    onChange,
}: Props) {
    const { t } = useTranslation();
    const { technical_asset_types: included, default_for_technical_asset_types: defaults } = value;

    const toggleIncluded = (type: string, checked: boolean) =>
        onChange?.({
            technical_asset_types: checked ? [...included, type] : included.filter((item) => item !== type),
            default_for_technical_asset_types: checked ? defaults : defaults.filter((item) => item !== type),
        });
    const toggleDefault = (type: string, checked: boolean) =>
        onChange?.({
            technical_asset_types: included,
            default_for_technical_asset_types: checked ? [...defaults, type] : defaults.filter((item) => item !== type),
        });

    const columns: ColumnsType<TechnicalAssetTypeOption> = [
        {
            title: t('Technical Asset type'),
            dataIndex: 'label',
        },
        {
            title: t('Included'),
            key: 'included',
            align: 'center',
            render: ({ label, value: type }: TechnicalAssetTypeOption) => (
                <Tooltip title={lockedTypes.get(type)}>
                    <Checkbox
                        aria-label={t('Include {{type}}', { type: label })}
                        checked={included.includes(type)}
                        disabled={lockedTypes.has(type)}
                        onChange={(event) => toggleIncluded(type, event.target.checked)}
                    />
                </Tooltip>
            ),
        },
        {
            title: t('Default'),
            key: 'default',
            align: 'center',
            render: ({ label, value: type }: TechnicalAssetTypeOption) => {
                const isIncluded = included.includes(type);
                const isOnlyDefault = isIncluded && !typesWithOtherDefault.has(type);
                return (
                    <Tooltip
                        title={
                            isOnlyDefault
                                ? t(
                                      "This is the default access mode for this type and can't be removed. Making another access mode the default replaces it.",
                                  )
                                : undefined
                        }
                    >
                        <Checkbox
                            aria-label={t('Default for {{type}}', { type: label })}
                            checked={isOnlyDefault || (isIncluded && defaults.includes(type))}
                            disabled={!isIncluded || isOnlyDefault}
                            onChange={(event) => toggleDefault(type, event.target.checked)}
                        />
                    </Tooltip>
                );
            },
        },
    ];

    return (
        <Table<TechnicalAssetTypeOption>
            dataSource={options}
            columns={columns}
            rowKey="value"
            pagination={false}
            size="small"
            loading={loading}
        />
    );
}
