import { Checkbox, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import QuestionTooltip from '@/components/tooltip/question-tooltip';
import type { EnvironmentGetItem } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    onToggleGlobal: (environment: EnvironmentGetItem, isGlobal: boolean) => void;
};

export const getEnvironmentTableColumns = ({ t, onToggleGlobal }: Props): TableColumnsType<EnvironmentGetItem> => {
    const sorter = new Sorter<EnvironmentGetItem>();
    return [
        {
            title: t('Name'),
            dataIndex: 'name',
            width: '33.33%',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            sorter: sorter.stringSorter((environment) => environment.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Acronym'),
            dataIndex: 'acronym',
            width: '33.33%',
            sorter: sorter.stringSorter((environment) => environment.acronym),
        },
        {
            title: (
                <QuestionTooltip
                    title={t(
                        'Domains that have not customized their own environment list automatically show all environments marked as global.',
                    )}
                >
                    {t('Global')}
                </QuestionTooltip>
            ),
            key: 'is_global',
            width: '33.33%',
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
                            'This environment will no longer show up for any domain that has not customized its own environment list. Continue?',
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
