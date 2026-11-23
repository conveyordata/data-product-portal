import { PostHogProvider } from '@posthog/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { Marketplace } from '@/pages/marketplace/marketplace.page.tsx';
import { mockDataProducts, mockDataProductsSearch } from '@/tests/mocks/dataProductsSearch.ts';
import { stubResizeObserver } from '@/tests/mocks/resizeObserver.ts';
import { act, renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const SEARCH_PLACEHOLDER = 'Ask a business question to find the relevant data';

function renderMarketplace() {
    renderWithProviders(
        <PostHogProvider client={posthog}>
            <Marketplace />
        </PostHogProvider>,
        { routerProps: { initialEntries: ['/marketplace'] } },
    );
}

describe('Marketplace', () => {
    beforeEach(() => {
        vi.spyOn(posthog, 'capture').mockImplementation(() => undefined);
    });

    afterEach(() => {
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

    it('shows the Data Products from the search', async () => {
        mockDataProductsSearch();
        renderMarketplace();

        expect(await screen.findByText(mockDataProducts[0].name)).toBeInTheDocument();
    });

    it('shows an empty state when no Data Products are found', async () => {
        mockDataProductsSearch([]);
        renderMarketplace();

        expect(await screen.findByText('No Data Products published yet')).toBeInTheDocument();
    });

    it('searches with the entered question', async () => {
        const queries: (string | null)[] = [];
        mockDataProductsSearch(mockDataProducts, (url) => queries.push(url.searchParams.get('query')));
        const user = userEvent.setup();
        renderMarketplace();

        await user.type(screen.getByPlaceholderText(SEARCH_PLACEHOLDER), 'campaign roi{enter}');

        await waitFor(() => expect(queries).toContain('campaign roi'));
        expect(posthog.capture).toHaveBeenCalledWith(PosthogEvents.MARKETPLACE_SEARCHED_DATA_PRODUCT, {
            search_term: 'campaign roi',
        });
    });

    it('does not send a search shorter than 3 characters', async () => {
        const queries: (string | null)[] = [];
        mockDataProductsSearch(mockDataProducts, (url) => queries.push(url.searchParams.get('query')));
        const user = userEvent.setup();
        renderMarketplace();

        await user.type(screen.getByPlaceholderText(SEARCH_PLACEHOLDER), 'ab{enter}');

        expect(
            await screen.findByText('Search only works when providing at least 3 characters as a search term'),
        ).toBeInTheDocument();
        expect(queries).not.toContain('ab');
        expect(posthog.capture).not.toHaveBeenCalled();
    });

    it('keeps the first visible Data Product on screen when fewer columns fit', async () => {
        const reportWidth = stubResizeObserver();
        mockDataProductsSearch(
            Array.from({ length: 30 }, (_, index) => ({
                ...mockDataProducts[0],
                id: `dp-${index + 1}`,
                name: `Data Product ${index + 1}`,
            })),
        );
        const user = userEvent.setup();
        renderMarketplace();
        await screen.findByText('Data Product 1');

        act(() => reportWidth(1600));
        await user.click(screen.getByLabelText('Page 3'));

        expect(await screen.findByText('Data Product 25')).toBeInTheDocument();

        act(() => reportWidth(900));

        expect(await screen.findByText('Data Product 25')).toBeInTheDocument();
        expect(screen.queryByText('Data Product 24')).not.toBeInTheDocument();
    });

    it('keeps the first visible Data Product on screen when more columns fit and the page falls out of range', async () => {
        const reportWidth = stubResizeObserver();
        mockDataProductsSearch(
            Array.from({ length: 30 }, (_, index) => ({
                ...mockDataProducts[0],
                id: `dp-${index + 1}`,
                name: `Data Product ${index + 1}`,
            })),
        );
        const user = userEvent.setup();
        renderMarketplace();
        await screen.findByText('Data Product 1');

        act(() => reportWidth(900));
        await user.click(screen.getByLabelText('Page 4'));

        expect(await screen.findByText('Data Product 19')).toBeInTheDocument();

        act(() => reportWidth(1600));

        expect(await screen.findByText('Data Product 19')).toBeInTheDocument();
        expect(screen.queryByText('Data Product 25')).not.toBeInTheDocument();
    });
});
