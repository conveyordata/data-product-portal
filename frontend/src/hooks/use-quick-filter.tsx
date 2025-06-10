import { GlobalOutlined, TeamOutlined } from '@ant-design/icons';
import { type RadioGroupProps, Space } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';

type Props = {
    initialQuickFilter?: QuickFilterParticipation;
};

export function useQuickFilter({ initialQuickFilter = QuickFilterParticipation.All }: Props) {
    const { t } = useTranslation();
    const [quickFilter, setQuickFilter] = useState(initialQuickFilter);

    const quickFilterOptions: RadioGroupProps['options'] = useMemo(
        () => [
            {
                label: (
                    <Space>
                        <GlobalOutlined />
                        {t('Show All')}
                    </Space>
                ),
                value: QuickFilterParticipation.All,
            },
            {
                label: (
                    <Space>
                        <TeamOutlined />
                        {t('Just Me')}
                    </Space>
                ),
                value: QuickFilterParticipation.Me,
            },
        ],
        [t],
    );

    const onQuickFilterChange = (value: QuickFilterParticipation) => {
        setQuickFilter(value);
    };

    return {
        quickFilter,
        onQuickFilterChange,
        quickFilterOptions,
    };
}
