declare global {
    namespace Cypress {
        interface Chainable {
            selectAntOption(labelText: string, optionText: string): Chainable<void>;
        }
    }
}

export {};
