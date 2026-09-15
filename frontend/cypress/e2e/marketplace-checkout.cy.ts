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

        cy.findByRole('searchbox', { name: /search/i }).type(`${outputPortName}{enter}`);
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.contains('[data-cy="output-port-card"]', outputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('[data-cy="output-port-card"]', outputPortName).within(() => {
            cy.get('[data-cy="add-to-cart"]').click();
        });

        cy.visit('/marketplace/cart');

        cy.findByText(outputPortName).should('be.visible');

        cy.get('[data-cy="checkout-build-data-products"]').click();
        cy.get('[data-cy="checkout-select-existing"]').click();

        cy.get('[data-cy="data-product-select"]').click();
        cy.get('[data-cy="data-product-select"]').find('input').type(consumingDataProductName);
        // The option also renders the data product's description, so its accessible name
        // is more than just the name: match it as a substring instead of an exact string.
        cy.findByRole('option', { name: new RegExp(consumingDataProductName) }).click();

        cy.get('[data-cy="justification"]').type('Needed for the Cypress end-to-end test.');

        cy.get('[data-cy="submit-access-requests"]').should('be.enabled').click();

        cy.findByText('Your requests have successfully been created.').should('be.visible');
    });

    it('lets a user search for a data product, add it to cart, and create a new exploration', () => {
        const explorationName = `Cypress E2E Exploration ${Date.now()}`;

        cy.intercept('GET', '**/v2/search/output_ports*').as('searchOutputPorts');
        cy.visit('/marketplace');
        // The Marketplace page fires an unfiltered search on mount. Wait for that
        // request to complete first, so the next cy.wait() below waits for our
        // actual search request instead of resolving on this earlier one.
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.findByRole('searchbox', { name: /search/i }).type(`${explorationOutputPortName}{enter}`);
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.contains('[data-cy="output-port-card"]', explorationOutputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('[data-cy="output-port-card"]', explorationOutputPortName).within(() => {
            cy.get('[data-cy="add-to-cart"]').click();
        });

        cy.visit('/marketplace/cart');

        cy.findByText(explorationOutputPortName).should('be.visible');

        cy.get('[data-cy="checkout-explore-data"]').click();
        cy.get('[data-cy="checkout-create-new"]').click();

        cy.get('[data-cy="exploration-name"]').type(explorationName);

        cy.get('[data-cy="exploration-domain-select"]').click();
        cy.findByRole('option', { name: explorationDomainName }).click();

        cy.get('[data-cy="justification"]').type('Needed for the Cypress end-to-end test.');

        cy.get('[data-cy="create-exploration"]').should('be.enabled').click();

        cy.findByText('Your Exploration has been created.').should('be.visible');
    });
});
