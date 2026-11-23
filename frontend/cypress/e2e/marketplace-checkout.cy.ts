const dataProductName = 'Customer Churn Prediction';
const outputPortName = 'Weekly Churn Probabilities';
const consumingDataProductName = 'DEI Insights Dashboard';

// A different Output Port of the same Data Product so this test doesn't interfere with the one above.
const explorationOutputPortName = 'Monthly Churn Targets';
const explorationDomainName = 'Customer Insights';

function addOutputPortToCart(name: string) {
    cy.intercept('GET', '**/v2/search/data_products*').as('searchDataProducts');
    cy.visit('/marketplace');
    // The Marketplace page fires an unfiltered search on mount. Wait for that
    // request to complete first, so the next cy.wait() below waits for our
    // actual search request instead of resolving on this earlier one.
    cy.wait('@searchDataProducts', { timeout: 30000 });

    cy.get('[data-cy="marketplace-search"]').type(`${dataProductName}{enter}`);
    cy.wait('@searchDataProducts', { timeout: 30000 });

    // The card container has no label of its own; its Data Product name scopes it.
    cy.contains('[data-cy="data-product-card"]', dataProductName, { timeout: 20000 }).within(() => {
        cy.contains('button', 'Add to cart').click();
    });

    cy.contains(name).click();
    cy.contains('button', 'Add 1 to cart').click();
}

describe('Marketplace checkout', () => {
    it('lets a user search for a data product, add it to cart, and request access', () => {
        addOutputPortToCart(outputPortName);

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

        addOutputPortToCart(explorationOutputPortName);

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
