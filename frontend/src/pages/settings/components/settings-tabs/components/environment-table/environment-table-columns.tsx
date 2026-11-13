import { Checkbox, InputNumber, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import QuestionTooltip from '@/components/tooltip/question-tooltip';
import type { EnvironmentGetItem } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    onToggleGlobal: (environment: EnvironmentGetItem, isGlobal: boolean) => void;
    onChangePosition: (environment: EnvironmentGetItem, position: number | null) => void;
    disabled?: boolean;
};

export const getEnvironmentTableColumns = ({
    t,
    onToggleGlobal,
    onChangePosition,
    disabled,
}: Props): TableColumnsType<EnvironmentGetItem> => {
    const sorter = new Sorter<EnvironmentGetItem>();
    return [
        {
            title: (
                <QuestionTooltip
                    title={t(
                        'Environments are listed in this order, lowest first. Environments without an order come last.',
                    )}
                >
                    {t('Order')}
                </QuestionTooltip>
            ),
            dataIndex: 'position',
            width: 120,
            sorter: sorter.numberSorter((environment) => environment.position ?? Number.MAX_SAFE_INTEGER),
            defaultSortOrder: 'ascend',
            render: (position: number | null | undefined, environment) => (
                <InputNumber
                    aria-label={t('Order of {{name}}', { name: environment.name })}
                    min={0}
                    precision={0}
                    disabled={disabled}
                    defaultValue={position ?? undefined}
                    onBlur={(event) => {
                        const next = event.target.value === '' ? null : Number(event.target.value);
                        if (next !== (position ?? null)) {
                            onChangePosition(environment, next);
                        }
                    }}
                />
            ),
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            width: '25%',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            sorter: sorter.stringSorter((environment) => environment.name),
        },
        {
            title: t('Acronym'),
            dataIndex: 'acronym',
            width: '25%',
            sorter: sorter.stringSorter((environment) => environment.acronym),
        },
        {
            title: (
                <QuestionTooltip
                    title={t(
                        'Environments marked as global are selected by default for new Data Products. Existing Data Products keep their declared environments.',
                    )}
                >
                    {t('Global')}
                </QuestionTooltip>
            ),
            key: 'is_global',
            width: '25%',
            render: (_, environment) => {
                const isGlobal = environment.is_global ?? true;
                if (!isGlobal) {
                    return (
                        <Checkbox checked={isGlobal} onChange={(e) => onToggleGlobal(environment, e.target.checked)} />
                    );
                }
                return (
                    <Popconfirm
                        title={t('Remove from global list')}
                        description={t(
                            'This environment will no longer be selected by default for new Data Products. Existing Data Products are not affected. Continue?',
                        )}
                        onConfirm={() => onToggleGlobal(environment, false)}
                        okText={t('Confirm')}
                        cancelText={t('Cancel')}
                    >
                        <Checkbox checked={isGlobal} />
                    </Popconfirm>
                );
            },
        },
    ];
};
