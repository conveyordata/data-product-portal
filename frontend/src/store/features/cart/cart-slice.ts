import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';

type CartState = {
    DatasetIds: string[];
};

const DATASET_IDS_KEY = 'CartDatasetIds';

const saveDatasetIds = (datasetIds: string[]): void => {
    localStorage.setItem(DATASET_IDS_KEY, JSON.stringify(datasetIds));
};

const loadDatasetIds = (): string[] => {
    try {
        const stored = localStorage.getItem(DATASET_IDS_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Failed to load dataset IDs from localStorage:', error);
        return [];
    }
};

const clearDatasetIds = (): void => {
    localStorage.removeItem(DATASET_IDS_KEY);
};

const cartSlice = createSlice({
    name: 'cart',
    initialState: { DatasetIds: loadDatasetIds() } as CartState,
    reducers: {
        addDatasetToCart: (
            state,
            {
                payload: { datasetId },
            }: PayloadAction<{
                datasetId: string;
            }>,
        ) => {
            if (state.DatasetIds.includes(datasetId)) {
                console.error('We tried to add a dataset id that is already in the cart');
                return;
            }
            state.DatasetIds = [...state.DatasetIds, datasetId];
            saveDatasetIds(state.DatasetIds);
        },
        removeDatasetFromCart: (
            state,
            {
                payload: { datasetId },
            }: PayloadAction<{
                datasetId: string;
            }>,
        ) => {
            state.DatasetIds = state.DatasetIds.filter((id) => id !== datasetId);
            saveDatasetIds(state.DatasetIds);
        },
        clearCart: (state) => {
            clearDatasetIds();
            state.DatasetIds = [];
        },
    },
    selectors: {
        selectCartDatasetIds: (state) => state.DatasetIds,
    },
});

export const { addDatasetToCart, removeDatasetFromCart, clearCart } = cartSlice.actions;

export default cartSlice.reducer;

export const { selectCartDatasetIds } = cartSlice.selectors;
