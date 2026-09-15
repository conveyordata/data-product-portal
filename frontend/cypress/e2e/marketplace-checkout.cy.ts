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

        cy.get('.ant-input-search input').type(outputPortName);
        cy.get('.ant-input-search input').should('have.value', outputPortName);
        cy.get('.ant-input-search input').type('{enter}');
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.contains('.ant-card', outputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('.ant-card', outputPortName).within(() => {
            cy.get('[data-cy="add-to-cart"]').click();
        });

        cy.visit('/marketplace/cart');

        cy.contains(outputPortName).should('be.visible');

        cy.get('[data-cy="checkout-build-data-products"]').click();
        cy.get('[data-cy="checkout-select-existing"]').click();

        cy.get('[data-cy="data-product-select"]').click();
        cy.get('[data-cy="data-product-select"]').find('input').type(consumingDataProductName);
        cy.get('.ant-select-dropdown')
            .should('be.visible')
            .within(() => {
                cy.contains(consumingDataProductName).click();
            });

        cy.get('[data-cy="justification"]').type('Needed for the Cypress end-to-end test.');

        cy.get('[data-cy="submit-access-requests"]').should('be.enabled').click();

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

        cy.get('.ant-input-search input').type(explorationOutputPortName);
        cy.get('.ant-input-search input').should('have.value', explorationOutputPortName);
        cy.get('.ant-input-search input').type('{enter}');
        cy.wait('@searchOutputPorts', { timeout: 30000 });

        cy.contains('.ant-card', explorationOutputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('.ant-card', explorationOutputPortName).within(() => {
            cy.get('[data-cy="add-to-cart"]').click();
        });

        cy.visit('/marketplace/cart');

        cy.contains(explorationOutputPortName).should('be.visible');

        cy.get('[data-cy="checkout-explore-data"]').click();
        cy.get('[data-cy="checkout-create-new"]').click();

        cy.get('[data-cy="exploration-name"]').type(explorationName);

        cy.get('[data-cy="exploration-domain-select"]').click();
        cy.get('.ant-select-dropdown')
            .should('be.visible')
            .within(() => {
                cy.contains(explorationDomainName).click();
            });

        cy.get('[data-cy="justification"]').type('Needed for the Cypress end-to-end test.');

        cy.get('[data-cy="create-exploration"]').should('be.enabled').click();

        cy.contains('Your Exploration has been created.').should('be.visible');
    });
});
