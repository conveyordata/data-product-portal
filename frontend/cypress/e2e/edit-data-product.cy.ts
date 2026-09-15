describe('Edit data product', () => {
    it('creates a data product and edits its name', () => {
        const originalName = `Cypress E2E Edit Target ${Date.now()}`;
        const updatedName = `${originalName} (edited)`;

        cy.visit('/studio/new');

        cy.intercept('GET', '**/resource_names/validate*').as('validateNamespace');
        cy.get('[data-cy="data-product-name"]').type(originalName);
        cy.get('[data-cy="namespace"]').should('not.have.value', '', { timeout: 10000 });
        cy.wait('@validateNamespace', { timeout: 10000 });

        cy.selectAntOption('data-product-type', 'Analytics');
        cy.selectAntOption('data-product-lifecycle', 'Draft');
        cy.selectAntOption('data-product-domain', 'Customer Insights');

        cy.get('[data-cy="data-product-description"]').type('Created by the Cypress end-to-end test, to be edited.');

        cy.intercept('POST', '**/v2/data_products').as('createDataProduct');
        cy.get('[data-cy="data-product-form-submit"]').should('be.enabled').click();
        cy.wait('@createDataProduct', { timeout: 30000 });
        cy.contains('Data Product created successfully').should('be.visible');

        cy.url().should('match', /\/studio\/[0-9a-f-]{36}/);
        cy.url().then((url) => {
            const dataProductId = url.split('/studio/')[1].split('?')[0];

            cy.visit(`/studio/${dataProductId}/edit`);

            cy.get('[data-cy="data-product-name"]').clear().type(updatedName);

            cy.intercept('PUT', `**/v2/data_products/${dataProductId}`).as('updateDataProduct');
            cy.get('[data-cy="data-product-form-submit"]').should('be.enabled').click();
            cy.wait('@updateDataProduct', { timeout: 30000 });

            cy.contains('Data Product updated successfully').should('be.visible');
            cy.url().should('match', new RegExp(`/studio/${dataProductId}`));
            cy.contains(updatedName).should('be.visible');
        });
    });
});
