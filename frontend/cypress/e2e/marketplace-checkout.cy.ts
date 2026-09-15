// This relies on backend/sample_data.sql being seeded, and specifically on
// "Weekly Churn Probabilities" not already being linked (as an input port) to
// "DEI Insights Dashboard" — if the seed data changes, update these fixtures.
const outputPortName = 'Weekly Churn Probabilities';
const consumingDataProductName = 'DEI Insights Dashboard';

// A different, unlinked output port so this test doesn't interfere with the one above.
const explorationOutputPortName = 'Monthly Churn Targets';
const explorationDomainName = 'Customer Insights';

describe('Marketplace checkout', () => {
    it('lets a user search for a data product, add it to cart, and request access', () => {
        cy.visit('/marketplace');

        cy.get('.ant-input-search input').type(outputPortName);
        cy.get('.ant-input-search input').should('have.value', outputPortName);
        cy.get('.ant-input-search input').type('{enter}');

        cy.contains('.ant-card', outputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('.ant-card', outputPortName).within(() => {
            cy.get('.ant-card-actions li').eq(1).find('button').click();
        });

        cy.visit('/marketplace/cart');

        cy.contains(outputPortName).should('be.visible');

        cy.contains('I want to build Data Products').click();
        cy.contains('Select an existing Data Product').click();

        cy.contains('label', 'Data Product').closest('.ant-form-item').find('.ant-select').click();
        // Type to filter the (virtualized) option list down, otherwise the target
        // option may not be rendered in the DOM yet and .contains() can't find it.
        cy.contains('label', 'Data Product').closest('.ant-form-item').find('input').type(consumingDataProductName);
        cy.get('.ant-select-dropdown')
            .should('be.visible')
            .within(() => {
                cy.contains(consumingDataProductName).click();
            });

        cy.contains('label', 'Business justification')
            .closest('.ant-form-item')
            .find('textarea')
            .type('Needed for the Cypress end-to-end test.');

        cy.contains('button', 'Submit access requests').should('be.enabled').click();

        cy.contains('Your requests have successfully been created.').should('be.visible');
    });

    it('lets a user search for a data product, add it to cart, and create a new exploration', () => {
        const explorationName = `Cypress E2E Exploration ${Date.now()}`;

        cy.visit('/marketplace');

        cy.get('.ant-input-search input').type(explorationOutputPortName);
        cy.get('.ant-input-search input').should('have.value', explorationOutputPortName);
        cy.get('.ant-input-search input').type('{enter}');

        cy.contains('.ant-card', explorationOutputPortName, { timeout: 20000 }).should('be.visible');

        cy.contains('.ant-card', explorationOutputPortName).within(() => {
            cy.get('.ant-card-actions li').eq(1).find('button').click();
        });

        cy.visit('/marketplace/cart');

        cy.contains(explorationOutputPortName).should('be.visible');

        cy.contains('I want to explore this data').click();
        cy.contains('Create a new Exploration').click();

        cy.contains('label', 'Name').closest('.ant-form-item').find('input').type(explorationName);

        cy.contains('label', 'Domain').closest('.ant-form-item').find('.ant-select').click();
        cy.get('.ant-select-dropdown')
            .should('be.visible')
            .within(() => {
                cy.contains(explorationDomainName).click();
            });

        cy.contains('label', 'Business justification')
            .closest('.ant-form-item')
            .find('textarea')
            .type('Needed for the Cypress end-to-end test.');

        cy.contains('button', 'Create').should('be.enabled').click();

        cy.contains('Your Exploration has been created.').should('be.visible');
    });
});
