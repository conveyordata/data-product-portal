describe('Role assignment', () => {
    it('grants a team member a role on a data product', () => {
        // "Access modes example" data product from backend/sample_data.sql; only the
        // default authenticated user is on its team, so Bob is always addable.
        const dataProductId = 'da9e4ef1-48d5-4f3d-9094-100d3abc64b5';
        const userName = 'Bob Johnson';

        cy.visit(`/studio/${dataProductId}?tab=team`);

        cy.contains('button', 'Add User').click();

        cy.get('[data-cy="user-popup-search"]').type(userName);

        cy.contains('[data-cy="user-popup-item"]', userName, { timeout: 20000 })
            .should('be.visible')
            .within(() => {
                cy.contains('Select a role').click({ force: true });
            });

        cy.intercept('POST', '**/authz/role_assignments/data_product').as('createRoleAssignment');
        cy.contains('Member').click();
        cy.wait('@createRoleAssignment', { timeout: 30000 });

        cy.contains('User has been granted access to the Data Product').should('be.visible');
    });
});
