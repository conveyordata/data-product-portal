describe('Output port management', () => {
    it('creates a new output port on an existing data product', () => {
        // "Access modes example" data product from backend/sample_data.sql; the
        // default authenticated user is its Owner, unlike e.g. Customer Segmentation.
        const dataProductId = 'da9e4ef1-48d5-4f3d-9094-100d3abc64b5';
        const outputPortName = `Cypress E2E Output Port ${Date.now()}`;

        cy.visit(`/studio/${dataProductId}?tab=outputs`);

        cy.contains('button', 'Add Output Port').click();

        cy.intercept('GET', '**/resource_names/validate*').as('validateNamespace');
        cy.get('.ant-modal').within(() => {
            cy.contains('label', 'Name').closest('.ant-form-item').find('input').type(outputPortName);

            // Namespace is derived from the name asynchronously; wait for it before submitting.
            cy.contains('label', 'Namespace')
                .closest('.ant-form-item')
                .find('input')
                .should('not.have.value', '', { timeout: 10000 });
        });
        // The namespace field is also validated asynchronously (debounced); wait for
        // that network call so the Create click isn't silently blocked mid-validation.
        cy.wait('@validateNamespace', { timeout: 10000 });

        cy.selectAntOption('Status', 'Draft');

        cy.get('.ant-modal').within(() => {
            cy.contains('label', 'Description')
                .closest('.ant-form-item')
                .find('textarea')
                .type('Created by the Cypress end-to-end test.');

            cy.intercept('POST', '**/output_ports').as('createOutputPort');
            cy.contains('button', 'Create').click();
        });
        cy.wait('@createOutputPort', { timeout: 30000 });

        cy.contains('Output Port created successfully').should('be.visible');
        cy.contains('.ant-card', outputPortName, { timeout: 20000 }).should('be.visible');
    });

    it('links an existing technical asset to an output port', () => {
        // "Access modes example" data product, with a technical asset deliberately
        // seeded as unlinked (backend/sample_data.sql).
        const dataProductId = 'da9e4ef1-48d5-4f3d-9094-100d3abc64b5';
        const outputPortName = 'Access mode example';
        const technicalAssetName = 'Access mode - 2 modes (unlinked output)';

        cy.visit(`/studio/${dataProductId}?tab=outputs`);

        cy.contains('.ant-card', outputPortName, { timeout: 20000 })
            .should('be.visible')
            .within(() => {
                cy.contains('button', 'Link Technical Assets').click();
            });

        cy.intercept('POST', '**/technical_assets/add').as('linkTechnicalAsset');
        cy.intercept('POST', '**/technical_assets/approve_link_request').as('approveTechnicalAssetLink');
        cy.get('.ant-modal').within(() => {
            cy.contains(technicalAssetName)
                .closest('.ant-list-item')
                .find('input[type="checkbox"]')
                .check({ force: true });

            cy.contains('button', /^Link \d+ assets?$/).click();
        });
        cy.wait('@linkTechnicalAsset', { timeout: 30000 });
        cy.wait('@approveTechnicalAssetLink', { timeout: 30000 });

        // The toast is transient and may already be gone by now; assert on the
        // resulting state instead, which is what actually matters.
        cy.get('.ant-modal').should('not.exist');
        cy.contains('.ant-card', outputPortName).contains('2 linked Technical Assets').should('be.visible');
    });
});
