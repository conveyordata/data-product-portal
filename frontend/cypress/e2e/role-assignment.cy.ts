describe('Role assignment', () => {
    it('grants a team member a role on a data product', () => {
        // "Access modes example" data product from backend/sample_data.sql; only the
        // default authenticated user is on its team, so Bob is always addable.
        const dataProductId = 'da9e4ef1-48d5-4f3d-9094-100d3abc64b5';
        const userName = 'Bob Johnson';

        cy.visit(`/studio/${dataProductId}?tab=team`);

        cy.contains('button', 'Add team member').click();

        // The search field has no visible label and shares its placeholder with the Team search.
        cy.get('[data-cy="identity-selector-search"]').type(userName);

        cy.contains('tr', userName, { timeout: 20000 })
            .should('be.visible')
            .within(() => {
                cy.contains('Select a role').click({ force: true });
            });

        cy.intercept('POST', '**/authz/role_assignments/data_product').as('createRoleAssignment');
        cy.contains('Member').click();
        cy.wait('@createRoleAssignment', { timeout: 30000 }).its('response.statusCode').should('eq', 200);

        cy.contains('Role has been assigned').should('be.visible');
        cy.contains('button', /^Cancel$/).click();
        cy.contains('tr', userName).within(() => {
            cy.contains('Member').should('be.visible');
            cy.contains('Approved').should('be.visible');
        });
    });
});
