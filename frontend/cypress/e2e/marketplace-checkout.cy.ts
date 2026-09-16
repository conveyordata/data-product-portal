const outputPortName = 'Weekly Churn Probabilities';
const consumingDataProductName = 'DEI Insights Dashboard';

// A different, unlinked output port so this test doesn't interfere with the one above.
const explorationOutputPortName = 'Monthly Churn Targets';
const explorationDomainName = 'Customer Insights';

describe('Marketplace checkout', () => {
    it('lets a user search for a data product, add it to cart, and request access', () => {
        cy.intercept('GET', '**/v2/search/output_ports*').as('searchOutputPorts');
        cy.visit('/marketplace');
        // The Marketplace page fires an unfiltered search on mount. Wait for that
        // request to complete first, so the next cy.wait() below waits for our
        // actual search request instead of resolving on this earlier one.
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.get('[data-cy="marketplace-search"]').type(`${outputPortName}{enter}`);
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.contains(outputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('[data-cy="output-port-card"]', outputPortName).within(() => {
            cy.get('[data-cy="add-to-cart"]').click();
        });

        cy.visit('/marketplace/cart');

        cy.contains(outputPortName).should('be.visible');

        cy.contains('I want to build Data Products').click();
        cy.contains('Select an existing Data Product').click();

        cy.contains('Search Data Products').click({ force: true });
        cy.focused().type(consumingDataProductName);
        cy.contains(consumingDataProductName).click();

        cy.contains('Business justification').click();
        cy.focused().type('Needed for the Cypress end-to-end test.');

        cy.contains('button', 'Submit access requests').should('be.enabled').click();

        cy.contains('Your requests have successfully been created.').should('be.visible');
    });

    it('lets a user search for a data product, add it to cart, and create a new exploration', () => {
        const explorationName = `Cypress E2E Exploration ${Date.now()}`;

        cy.intercept('GET', '**/v2/search/output_ports*').as('searchOutputPorts');
        cy.visit('/marketplace');
        // The Marketplace page fires an unfiltered search on mount. Wait for that
        // request to complete first, so the next cy.wait() below waits for our
        // actual search request instead of resolving on this earlier one.
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.get('[data-cy="marketplace-search"]').type(`${explorationOutputPortName}{enter}`);
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.contains(explorationOutputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('[data-cy="output-port-card"]', explorationOutputPortName).within(() => {
            cy.get('[data-cy="add-to-cart"]').click();
        });

        cy.visit('/marketplace/cart');

        cy.contains(explorationOutputPortName).should('be.visible');

        cy.contains('I want to explore this data').click();
        cy.contains('Create a new Exploration').click();

        cy.contains('Name').click();
        cy.focused().type(explorationName);

        cy.contains('Search domains').click({ force: true });
        cy.contains(explorationDomainName).click();

        cy.contains('Business justification').click();
        cy.focused().type('Needed for the Cypress end-to-end test.');

        cy.contains('button', 'Create').should('be.enabled').click();

        cy.contains('Your Exploration has been created.').should('be.visible');
    });
});
