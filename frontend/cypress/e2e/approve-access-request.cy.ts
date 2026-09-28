describe('Approve pending access request', () => {
    it('approves a pending input port access request', () => {
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
