import { Typography } from 'antd';
import { useMemo } from 'react';

import { useMainAIEndpointQuery } from '@/store/features/agentic-system/agentic-system-api-slice';

export function AgenticSystem() {
    const { data: agenticSystem } = useMainAIEndpointQuery();

    const result = useMemo(() => {
        console.log(agenticSystem);
        return agenticSystem?.message;
    }, [agenticSystem]);

    return <Typography.Title>{result}</Typography.Title>;
}
