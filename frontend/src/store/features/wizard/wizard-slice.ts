import { createSlice } from '@reduxjs/toolkit';

const wizardSlice = createSlice({
    name: 'wizard',
    initialState: {
        wizardEnabled: false,
    },
    reducers: {
        toggleWizard: (state) => {
            // Redux Toolkit uses Immer under the hood, allowing "mutating" logic
            state.wizardEnabled = !state.wizardEnabled;
        },
        // Optional: If you ever need to set it to a specific boolean directly
        setWizardEnabled: (state, action) => {
            state.wizardEnabled = action.payload;
        },
    },
    selectors: {
        selectWizardEnabled: (state) => state.wizardEnabled,
    },
});

export const { toggleWizard, setWizardEnabled } = wizardSlice.actions;
export const { selectWizardEnabled } = wizardSlice.selectors;
export default wizardSlice.reducer;
