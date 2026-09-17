Cypress.Commands.add('selectAntOption', (dataCy: string, optionText: string) => {
    cy.get(`[data-cy="${dataCy}"]`).click();
    cy.get(`[data-cy="${dataCy}-options"]`).contains(optionText).click();
});

export {};
