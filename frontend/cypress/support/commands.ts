Cypress.Commands.add('selectAntOption', (dataCy: string, optionText: string) => {
    cy.get(`[data-cy="${dataCy}"]`).click();
    cy.contains(optionText).click();
});

export {};
