describe('Explorer page', () => {
    it('renders the data product graph with at least one node', () => {
        cy.visit('/explorer');

        cy.contains('h1, h2, h3', 'Explorer').should('be.visible');

        // The graph is rendered by @xyflow/react once the graph data query resolves.
        cy.get('.react-flow__node', { timeout: 20000 }).should('have.length.greaterThan', 0);
    });
});
