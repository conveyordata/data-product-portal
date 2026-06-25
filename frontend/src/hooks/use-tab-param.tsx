import { useCallback } from 'react';
import { useSearchParams } from 'react-router';

export type Props = {
    defaultValue: string;
    acceptedValues?: string[];
};
export function useTabParam(defaultValue: string, acceptedValues?: string[], capturePosthog?: (value: string) => void) {
    const [searchParams, setSearchParams] = useSearchParams();

    const onTabChange = useCallback(
        (key: string) => {
            capturePosthog?.(key);
            setSearchParams({ tab: key });
        },
        [setSearchParams, capturePosthog],
    );

    const resolveTab = useCallback(() => {
        const tab = searchParams.get('tab') ?? defaultValue;
        if (acceptedValues?.includes(tab)) {
            return tab;
        }
        return defaultValue;
    }, [searchParams, defaultValue, acceptedValues]);

    const activeTab = resolveTab();

    return { activeTab, onTabChange };
}
