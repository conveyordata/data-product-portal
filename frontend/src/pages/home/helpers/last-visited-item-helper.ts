import type { LastVisitedItem } from '@/utils/local-storage.helper.ts';

export const getLastVisitedItemTimestamp = (lastVisitedItems: LastVisitedItem[], itemId: string) => {
    const lastVisited = lastVisitedItems.find((lastVisited) => lastVisited.id === itemId);
    return lastVisited?.timestamp;
};

export const getLastVisitedItemDate = (lastVisitedItems: LastVisitedItem[], itemId: string): Date | undefined => {
    const timestamp = getLastVisitedItemTimestamp(lastVisitedItems, itemId);
    return timestamp ? new Date(timestamp) : undefined;
};

export const filterOutNonMatchingItems = <
    T extends {
        id: string;
    },
>(
    lastVisitedItems: LastVisitedItem[],
    items: T[] = [],
): T[] => {
    if (!lastVisitedItems.length) {
        return [];
    }
    return lastVisitedItems
        .map((lastVisited) => {
            return items.find((item) => item.id === lastVisited.id);
        })
        .filter((item) => !!item)
        .sort((a, b) => {
            if (!a || !b) {
                return 0;
            }
            return (
                (getLastVisitedItemTimestamp(lastVisitedItems, b.id) || 0) -
                (getLastVisitedItemTimestamp(lastVisitedItems, a.id) || 0)
            );
        }) as T[];
};

export const sortLastVisitedOwnedItems = <
    T extends {
        id: string;
    },
>(
    lastVisitedItems: LastVisitedItem[],
    items: T[] = [],
): T[] => {
    if (!lastVisitedItems.length) {
        return items;
    }
    const copy = [...items];

    copy.sort((a, b) => {
        const aTimestamp = getLastVisitedItemTimestamp(lastVisitedItems, a.id) || 0;
        const bTimestamp = getLastVisitedItemTimestamp(lastVisitedItems, b.id) || 0;
        return bTimestamp - aTimestamp;
    });

    return copy;
};
