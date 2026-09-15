// Relies on backend/sample_data.sql seeding the "Analytics" data product type,
// "Draft" lifecycle and "Customer Insights" domain.
describe('Create data product', () => {
    it('creates a new data product and lands on its detail page', () => {
        const dataProductName = `Cypress E2E Data Product ${Date.now()}`;

        cy.visit('/studio/new');

        cy.intercept('GET', '**/resource_names/validate*').as('validateNamespace');
        cy.contains('label', 'Name').closest('.ant-form-item').find('input').type(dataProductName);

        // Namespace is derived from the name asynchronously; wait for it before submitting.
        cy.contains('label', 'Namespace')
            .closest('.ant-form-item')
            .find('input')
            .should('not.have.value', '', { timeout: 10000 });
        // The namespace field is also validated asynchronously (debounced); wait for
        // that network call so the Create click isn't silently blocked mid-validation.
        cy.wait('@validateNamespace', { timeout: 10000 });

        cy.selectAntOption('Type', 'Analytics');
        cy.selectAntOption('Status', 'Draft');
        cy.selectAntOption('Domain', 'Customer Insights');

        cy.contains('label', 'Description')
            .closest('.ant-form-item')
            .find('textarea')
            .type('Created by the Cypress end-to-end test.');

        cy.intercept('POST', '**/v2/data_products').as('createDataProduct');
        cy.contains('button', 'Create').should('be.enabled').click();
        cy.wait('@createDataProduct', { timeout: 30000 });

        cy.contains('Data Product created successfully').should('be.visible');
        cy.url().should('match', /\/studio\/[0-9a-f-]{36}/);
        cy.contains(dataProductName).should('be.visible');
    });
});
