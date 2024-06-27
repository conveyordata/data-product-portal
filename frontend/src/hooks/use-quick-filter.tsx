import { useMemo, useState } from 'react';
import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';
import { RadioGroupProps, Space } from 'antd';
import { GlobalOutlined, TeamOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

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
