import { http } from 'msw';
import { describe, expect, it } from 'vitest';
import { PeoplePage } from '@/pages/people/people-table.component';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users';
import { server } from '../../mocks/server';
import { renderWithProviders, screen, userEvent, waitFor } from '../../test-utils';

describe('PeoplePage', () => {
    it('shows loading state while fetching', () => {
        server.use(
            http.get('*/api/v2/users', () => {
                return new Promise(() => {
                    // Never resolve call
                });
            }),
        );
        const { container } = renderWithProviders(<PeoplePage />);

        expect(container.querySelector('.ant-spin-spinning')).toBeInTheDocument();
    });
    it('renders an empty table when there are no users', async () => {
        mockUsersHttp([]);
        renderWithProviders(<PeoplePage />);

        await waitFor(() => {
            expect(screen.getByText('People')).toBeInTheDocument();
        });

        const table = screen.getByTestId('people-table');
        const description = table.querySelector('.ant-empty-description');
        expect(description).toHaveTextContent('No data');
    });

    it('displays users returned by the API', async () => {
        mockUsersHttp([mockUsers[0], mockUsers[1]]);
        renderWithProviders(<PeoplePage />);
        const user1 = 'alice@example.com';
        const user2 = 'bob@example.com';

        await waitFor(() => {
            expect(screen.getByText(user1)).toBeInTheDocument();
        });
        expect(screen.getByText(user1)).toBeInTheDocument();
        expect(screen.getByText(user2)).toBeInTheDocument();
    });

    it('filters users by search term', async () => {
        mockUsersHttp([mockUsers[0], mockUsers[1]]);
        renderWithProviders(<PeoplePage />);
        const user1 = 'alice@example.com';

        await waitFor(() => {
            expect(screen.getByText(user1)).toBeInTheDocument();
        });

        const searchInput = screen.getByPlaceholderText('Search people by name');
        await userEvent.type(searchInput, 'bob');

        await waitFor(() => {
            expect(screen.queryByText(user1)).not.toBeInTheDocument();
        });
        expect(screen.getByText('bob@example.com')).toBeInTheDocument();
    });
});
