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

type CartOutputPort = {
    outputPortId: string;
    accessModeId?: string;
};

type CartState = {
    outputPortIds: CartOutputPort[];
    dataProductTypeChoice: DataProductChoiceOptions | null;
    existingOrNewChoice: ExistingOrNew | null;
};

const OUTPUT_PORT_IDS_KEY = 'CartOutputPortIds';
const EXPLORATION_CHOICES_KEY = 'CartExplorationChoices';

const saveOutputPortIds = (outputPorts: CartOutputPort[]): void => {
    localStorage.setItem(OUTPUT_PORT_IDS_KEY, JSON.stringify(outputPorts));
};

const loadOutputPortIds = (): CartOutputPort[] => {
    try {
        const stored = localStorage.getItem(OUTPUT_PORT_IDS_KEY);
        if (!stored) {
            return [];
        }

        const parsed: unknown = JSON.parse(stored);
        return Array.isArray(parsed) ? (parsed as CartOutputPort[]) : [];
    } catch (error) {
        console.error('Failed to load output port IDs from localStorage:', error);
        return [];
    }
};

const clearOutputPortIds = (): void => {
    localStorage.removeItem(OUTPUT_PORT_IDS_KEY);
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
        outputPortIds: loadOutputPortIds(),
        dataProductTypeChoice: initialDataProductTypeChoice,
        existingOrNewChoice: initialExistingOrNewChoice,
    } as CartState,
    reducers: {
        addOutputPortToCart: (
            state,
            {
                payload: { outputPortId, accessModeId },
            }: PayloadAction<{
                outputPortId: string;
                accessModeId?: string;
            }>,
        ) => {
            if (state.outputPortIds.some((item) => item.outputPortId === outputPortId)) {
                console.error('We tried to add an output port that is already in the cart');
                return;
            }

            state.outputPortIds = [...state.outputPortIds, { outputPortId, accessModeId }];
            saveOutputPortIds(state.outputPortIds);
        },
        removeOutputPortFromCart: (
            state,
            {
                payload: { outputPortId },
            }: PayloadAction<{
                outputPortId: string;
            }>,
        ) => {
            state.outputPortIds = state.outputPortIds.filter((item) => item.outputPortId !== outputPortId);
            saveOutputPortIds(state.outputPortIds);
        },
        selectAccessModeForOutputPortInCart: (
            state,
            {
                payload: { outputPortId, accessModeId },
            }: PayloadAction<{
                outputPortId: string;
                accessModeId: string;
            }>,
        ) => {
            const outputPortExists = state.outputPortIds.some((item) => item.outputPortId === outputPortId);
            if (!outputPortExists) {
                console.error('We tried to select an access mode for an output port that is not in the cart');
                return;
            }

            state.outputPortIds = state.outputPortIds.map((item) =>
                item.outputPortId === outputPortId ? { ...item, accessModeId } : item,
            );
            saveOutputPortIds(state.outputPortIds);
        },
        clearCart: (state) => {
            clearOutputPortIds();
            clearExplorationChoicesStorage();
            state.outputPortIds = [];
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
        selectCartOutputPortIds: (state) => state.outputPortIds.map((item) => item.outputPortId),
        selectCartOutputPorts: (state) => state.outputPortIds,
        selectCartDataProductTypeChoice: (state) => state.dataProductTypeChoice,
        selectCartExistingOrNewChoice: (state) => state.existingOrNewChoice,
    },
});

export const {
    addOutputPortToCart,
    removeOutputPortFromCart,
    selectAccessModeForOutputPortInCart,
    clearCart,
    setCartExplorationChoices,
} = cartSlice.actions;

export default cartSlice.reducer;

export const {
    selectCartOutputPortIds,
    selectCartOutputPorts,
    selectCartDataProductTypeChoice,
    selectCartExistingOrNewChoice,
} = cartSlice.selectors;
