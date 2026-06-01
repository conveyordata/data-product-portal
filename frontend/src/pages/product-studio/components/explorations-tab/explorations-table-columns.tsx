import type { TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { Domain, Exploration } from '@/store/api/services/generated/explorationsApi.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

export const getExplorationTableColumns = ({
    t,
    explorations,
}: {
    t: TFunction;
    explorations: Exploration[];
}): TableColumnsType<Exploration> => {
    const sorter = new Sorter<Exploration>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: {
                showTitle: false,
            },
            render: (name) => {
                return <TableCellItem text={name} tooltip={{ content: name }} />;
            },
            sorter: sorter.stringSorter((dp) => dp.name),
            defaultSortOrder: 'ascend',
            width: '25%',
        },
        {
            title: t('Domain'),
            dataIndex: 'domain',
            render: (domain: Domain) => {
                return <TableCellItem text={domain.name} />;
            },
            ...new FilterSettings(explorations, (dp) => dp.domain.name),
            sorter: sorter.stringSorter((dp) => dp.domain.name),
        },
    ];
};
