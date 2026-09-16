describe('Explorer page', () => {
    it('renders the data product graph with at least one node', () => {
        cy.visit('/explorer');

        cy.contains('Explorer').should('be.visible');

        // The graph is rendered by @xyflow/react once the graph data query resolves.
        cy.get('[data-cy="graph-node"]', { timeout: 20000 }).should('have.length.greaterThan', 0);
        cy.get('[data-cy="graph-edge"]').should('have.length.greaterThan', 0);
    });
});
