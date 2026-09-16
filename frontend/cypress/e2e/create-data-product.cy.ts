describe('Create data product', () => {
    it('creates a new data product and lands on its detail page', () => {
        const dataProductName = `Cypress E2E Data Product ${Date.now()}`;

        cy.visit('/studio/new');

        cy.intercept('GET', '**/resource_names/validate*').as('validateNamespace');
        cy.get('[data-cy="data-product-name"]').type(dataProductName);

        cy.get('[data-cy="namespace"]').should('not.have.value', '', { timeout: 10000 });
        cy.wait('@validateNamespace', { timeout: 10000 });

        cy.selectAntOption('data-product-type', 'Analytics');
        cy.selectAntOption('data-product-lifecycle', 'Draft');
        cy.selectAntOption('data-product-domain', 'Customer Insights');

        cy.get('[data-cy="data-product-description"]').type('Created by the Cypress end-to-end test.');

        cy.intercept('POST', '**/v2/data_products').as('createDataProduct');
        cy.contains('button', 'Create').should('be.enabled').click();
        cy.wait('@createDataProduct', { timeout: 30000 });

        cy.contains('Data Product created successfully').should('be.visible');
        cy.url().should('match', /\/studio\/[0-9a-f-]{36}/);
        cy.contains(dataProductName).should('be.visible');
    });
});
