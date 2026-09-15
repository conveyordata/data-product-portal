Cypress.Commands.add('selectAntOption', (labelText: string, optionText: string) => {
    cy.contains('label', labelText).closest('.ant-form-item').find('.ant-select').click();
    cy.get('.ant-select-dropdown')
        .filter(':visible')
        .last()
        .within(() => {
            cy.contains(optionText).click();
        });
});

export {};
