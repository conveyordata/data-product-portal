import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';

export enum DataProductChoiceOptions {
    exploration = 'EXPLORATION',
    data_product = 'DATA_PRODUCT',
}

export enum ExistingOrNew {
    existing = 'EXISTING',
    new = 'new',
}

export type CartState = {
    DatasetIds: string[];
    dataProductTypeChoice: DataProductChoiceOptions | null;
    existingOrNewChoice: ExistingOrNew | null;
};

const DATASET_IDS_KEY = 'CartDatasetIds';
const EXPLORATION_CHOICES_KEY = 'CartExplorationChoices';

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

const saveExplorationChoices = (dataProductTypeChoice: string | null, existingOrNewChoice: string | null): void => {
    localStorage.setItem(EXPLORATION_CHOICES_KEY, JSON.stringify({ dataProductTypeChoice, existingOrNewChoice }));
};

const loadExplorationChoices = (): { dataProductTypeChoice: string | null; existingOrNewChoice: string | null } => {
    try {
        const stored = localStorage.getItem(EXPLORATION_CHOICES_KEY);
        return stored ? JSON.parse(stored) : { dataProductTypeChoice: null, existingOrNewChoice: null };
    } catch {
        return { dataProductTypeChoice: null, existingOrNewChoice: null };
    }
};

const clearExplorationChoicesStorage = (): void => {
    localStorage.removeItem(EXPLORATION_CHOICES_KEY);
};

const { dataProductTypeChoice: initialDataProductTypeChoice, existingOrNewChoice: initialExistingOrNewChoice } =
    loadExplorationChoices();

const cartSlice = createSlice({
    name: 'cart',
    initialState: {
        DatasetIds: loadDatasetIds(),
        dataProductTypeChoice: initialDataProductTypeChoice,
        existingOrNewChoice: initialExistingOrNewChoice,
    } as CartState,
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
            clearExplorationChoicesStorage();
            state.DatasetIds = [];
            state.dataProductTypeChoice = null;
            state.existingOrNewChoice = null;
        },
        setCartExplorationChoices: (
            state,
            {
                payload: { dataProductTypeChoice, existingOrNewChoice },
            }: PayloadAction<{
                dataProductTypeChoice: DataProductChoiceOptions | null;
                existingOrNewChoice: ExistingOrNew | null;
            }>,
        ) => {
            state.dataProductTypeChoice = dataProductTypeChoice;
            state.existingOrNewChoice = existingOrNewChoice;
            saveExplorationChoices(dataProductTypeChoice, existingOrNewChoice);
        },
    },
    selectors: {
        selectCartDatasetIds: (state) => state.DatasetIds,
        selectCartDataProductTypeChoice: (state) => state.dataProductTypeChoice,
        selectCartExistingOrNewChoice: (state) => state.existingOrNewChoice,
    },
});

export const { addDatasetToCart, removeDatasetFromCart, clearCart, setCartExplorationChoices } = cartSlice.actions;

export default cartSlice.reducer;

export const { selectCartDatasetIds, selectCartDataProductTypeChoice, selectCartExistingOrNewChoice } =
    cartSlice.selectors;
