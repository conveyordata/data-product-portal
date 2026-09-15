declare global {
    namespace Cypress {
        interface Chainable {
            selectAntOption(dataCy: string, optionText: string): Chainable<void>;
        }
    }
}

export {};
