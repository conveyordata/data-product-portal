// IDs from backend/sample_data.sql — requires the local DB to be seeded via
// `poetry run python -m app.db_tool init sample_data.sql`.
const dataProductId = '138d83af-7a12-4037-85e7-fab3383593f2'; // Customer Segmentation
const outputPortId = '811cd818-3b0d-437a-96bd-f29cbb3449d2'; // Customer Segments Weekly

describe('Detail pages', () => {
    it('loads the data product detail page', () => {
        cy.visit(`/studio/${dataProductId}`);

        cy.contains('Customer Segmentation').should('be.visible');
    });

    it('loads the output port detail page', () => {
        cy.visit(`/studio/${dataProductId}/output-port/${outputPortId}`);

        cy.contains('Customer Segments Weekly').should('be.visible');
    });
});
