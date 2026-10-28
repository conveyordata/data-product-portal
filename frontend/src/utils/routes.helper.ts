import type { DynamicPathParams } from '@/types/navigation.ts';

export function getDynamicRoutePath(path: string, param: DynamicPathParams, value: string) {
    return path.replace(`:${param}`, value);
}
