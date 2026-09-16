describe('Approve pending access request', () => {
    it('approves a pending input port access request', () => {
        // Seeded PENDING request in backend/sample_data.sql: "Financial Risk Assessment"
        // requesting access to the "Daily Feature Engagement" output port, owned by the
        // default authenticated user.
        const requestDescription = 'Financial Risk Assessment requests read access to Daily Feature Engagement';

        cy.visit('/studio?tab=pending-requests');

        cy.contains('[data-cy="pending-request-row"]', requestDescription, { timeout: 20000 })
            .should('be.visible')
            .within(() => {
                cy.contains('button', 'Review').click();
            });

        cy.contains('button', 'Accept').should('be.visible');

        cy.intercept('POST', '**/input_ports/approve').as('approveInputPort');
        cy.contains('button', 'Accept').click();
        cy.wait('@approveInputPort', { timeout: 30000 });

        cy.contains('Output Port request has been successfully approved').should('be.visible');
    });
});
