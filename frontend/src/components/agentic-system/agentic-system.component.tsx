import { useMainAIEndpointQuery } from '@/store/features/agentic-system/agentic-system-api-slice';
import { Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

type Props = {};

export function AgenticSystem({}: Props) {
    const { t } = useTranslation();
    const { data: agenticSystem, isFetching } = useMainAIEndpointQuery();

    const result = useMemo(() => {
        console.log(agenticSystem);
        return agenticSystem?.message;
    }, [agenticSystem]);

    return <Typography.Title>{result}</Typography.Title>;
}
