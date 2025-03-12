import { Radio, RadioChangeEvent, RadioGroupProps } from 'antd';

import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';

type QuickFiltersProps = {
    value: QuickFilterParticipation;
    onFilterChange: (e: RadioChangeEvent) => void;
    quickFilterOptions: RadioGroupProps['options'];
};

export function TableQuickFilter({ value, onFilterChange, quickFilterOptions }: QuickFiltersProps) {
    return (
        <Radio.Group
            value={value}
            options={quickFilterOptions}
            onChange={onFilterChange}
            optionType="button"
            buttonStyle="solid"
            size={'middle'}
        />
    );
}
