describe('Edit data product', () => {
    it('creates a data product and edits its name', () => {
        const originalName = `Cypress E2E Edit Target ${Date.now()}`;
        const updatedName = `${originalName} (edited)`;

        cy.visit('/studio/new');

        cy.intercept('GET', '**/resource_names/validate*').as('validateNamespace');
        cy.contains('label', 'Name').closest('.ant-form-item').find('input').type(originalName);
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
            .type('Created by the Cypress end-to-end test, to be edited.');

        cy.intercept('POST', '**/v2/data_products').as('createDataProduct');
        cy.contains('button', 'Create').should('be.enabled').click();
        cy.wait('@createDataProduct', { timeout: 30000 });
        cy.contains('Data Product created successfully').should('be.visible');

        cy.url().should('match', /\/studio\/[0-9a-f-]{36}/);
        cy.url().then((url) => {
            const dataProductId = url.split('/studio/')[1].split('?')[0];

            cy.visit(`/studio/${dataProductId}/edit`);

            cy.contains('label', 'Name').closest('.ant-form-item').find('input').clear().type(updatedName);

            cy.intercept('PUT', `**/v2/data_products/${dataProductId}`).as('updateDataProduct');
            cy.contains('button', 'Save').should('be.enabled').click();
            cy.wait('@updateDataProduct', { timeout: 30000 });

            cy.contains('Data Product updated successfully').should('be.visible');
            cy.url().should('match', new RegExp(`/studio/${dataProductId}`));
            cy.contains(updatedName).should('be.visible');
        });
    });
});
