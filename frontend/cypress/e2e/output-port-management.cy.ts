describe('Output port management', () => {
    it('creates a new output port on an existing data product', () => {
        // "Access modes example" data product from backend/sample_data.sql; the
        // default authenticated user is its Owner, unlike e.g. Customer Segmentation.
        const dataProductId = 'da9e4ef1-48d5-4f3d-9094-100d3abc64b5';
        const outputPortName = `Cypress E2E Output Port ${Date.now()}`;

        cy.visit(`/studio/${dataProductId}?tab=outputs`);

        cy.contains('button', 'Add Output Port').click();

        cy.intercept('GET', '**/resource_names/validate*').as('validateNamespace');
        cy.get('[data-cy="output-port-name"]').type(outputPortName);
        cy.get('[data-cy="namespace"]').should('not.have.value', '', { timeout: 10000 });
        cy.wait('@validateNamespace', { timeout: 10000 });

        cy.selectAntOption('output-port-lifecycle', 'Draft');

        cy.get('[data-cy="output-port-description"]').type('Created by the Cypress end-to-end test.');

        cy.intercept('POST', '**/output_ports').as('createOutputPort');
        cy.contains('button', 'Create').click();
        cy.wait('@createOutputPort', { timeout: 30000 });

        cy.contains('Output Port created successfully').should('be.visible');
        cy.contains('[data-cy="output-port-card"]', outputPortName, { timeout: 20000 }).should('be.visible');
    });

    it('links an existing technical asset to an output port', () => {
        // "Access modes example" data product, with a technical asset deliberately
        // seeded as unlinked (backend/sample_data.sql).
        const dataProductId = 'da9e4ef1-48d5-4f3d-9094-100d3abc64b5';
        const outputPortName = 'Access mode example';
        const technicalAssetName = 'Access mode - 2 modes (unlinked output)';

        cy.visit(`/studio/${dataProductId}?tab=outputs`);

        cy.contains('[data-cy="output-port-card"]', outputPortName, { timeout: 20000 })
            .should('be.visible')
            .within(() => {
                cy.contains('button', 'Link Technical Assets').click();
            });

        cy.intercept('POST', '**/technical_assets/add').as('linkTechnicalAsset');
        cy.intercept('POST', '**/technical_assets/approve_link_request').as('approveTechnicalAssetLink');
        cy.contains('[data-cy="technical-asset-link-item"]', technicalAssetName)
            .find('input[type="checkbox"]')
            .check({ force: true });
        cy.contains('button', /Link \d+ assets?/).click();
        cy.wait('@linkTechnicalAsset', { timeout: 30000 });
        cy.wait('@approveTechnicalAssetLink', { timeout: 30000 });

        // The toast is transient and may already be gone by now; assert on the
        // resulting state instead, which is what actually matters.
        cy.contains(`Link Technical Assets to ${outputPortName}`).should('not.be.visible');
        cy.contains('[data-cy="output-port-card"]', outputPortName)
            .contains('2 linked Technical Assets')
            .should('be.visible');
    });
});
