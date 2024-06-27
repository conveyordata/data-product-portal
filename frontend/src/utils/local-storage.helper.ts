export enum LocalStorageKeys {
    LastVisitedDataProducts = 'lastVisitedDataProducts',
    LastVisitedDatasets = 'lastVisitedDatasets',
}

export enum AppVersion {
    V0_1 = 'v0.1',
}

const currentAppVersion = AppVersion.V0_1;

export interface LastVisitedItem {
    id: string;
    timestamp: number;
    version: AppVersion;
}

export const setItemToLocalStorage = (key: LocalStorageKeys, item: Omit<LastVisitedItem, 'version'>) => {
    const existingItems = getItemFromLocalStorage(key);
    const existingItemIndex = existingItems.findIndex(
        (existingItem) => existingItem.id === item.id && existingItem.version === currentAppVersion,
    );

    if (existingItemIndex !== -1) {
        existingItems.splice(existingItemIndex, 1);
    }

    existingItems.push({
        ...item,
        version: currentAppVersion,
    });
    localStorage.setItem(key, JSON.stringify(existingItems));
};

export const getItemFromLocalStorage = (key: LocalStorageKeys, shouldIgnoreVersion = false): LastVisitedItem[] => {
    const storedItems = localStorage.getItem(key);
    const parsedItems = storedItems ? JSON.parse(storedItems) : [];

    if (shouldIgnoreVersion) {
        return parsedItems;
    }

    return parsedItems.filter((item: LastVisitedItem) => item.version === currentAppVersion);
};
