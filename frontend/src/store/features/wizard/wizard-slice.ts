import { createSlice } from '@reduxjs/toolkit';

const wizardSlice = createSlice({
    name: 'wizard',
    initialState: {
        wizardEnabled: false,
    },
    reducers: {
        toggleWizard: (state) => {
            state.wizardEnabled = !state.wizardEnabled;
        },
    },
    selectors: {
        selectWizardEnabled: (state) => state.wizardEnabled,
    },
});

export const { toggleWizard } = wizardSlice.actions;
export const { selectWizardEnabled } = wizardSlice.selectors;
export default wizardSlice.reducer;
