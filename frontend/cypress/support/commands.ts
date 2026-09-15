Cypress.Commands.add('selectAntOption', (dataCy: string, optionText: string) => {
    cy.get(`[data-cy="${dataCy}"]`).click();
    cy.get('.ant-select-dropdown')
        .filter(':visible')
        .last()
        .within(() => {
            cy.contains(optionText).click();
        });
});

export {};
