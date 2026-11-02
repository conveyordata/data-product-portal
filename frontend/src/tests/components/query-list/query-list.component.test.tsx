import { describe, expect, it, vi } from 'vitest';
import type { EmptyStateQuery } from '@/components/empty-state/empty-state.component.tsx';
import { QueryList } from '@/components/query-list/query-list.component.tsx';
import { renderWithProviders, screen } from '../../test-utils';

const settledQuery: EmptyStateQuery = {
    isFetching: false,
    isUninitialized: false,
    isError: false,
    currentData: [],
    refetch: vi.fn(),
};

function renderList(query: Partial<EmptyStateQuery>) {
    return renderWithProviders(
        <QueryList
            query={{ ...settledQuery, ...query }}
            items={['Sales Analytics']}
            renderItem={(name) => <p key={name}>{name}</p>}
            subject="Output Ports"
            emptyState={{ icon: <span />, title: 'No Output Ports yet' }}
        />,
    );
}

describe('QueryList', () => {
    it('shows the items once data for the current arguments is loaded', () => {
        renderList({});

        expect(screen.getByText('Sales Analytics')).toBeInTheDocument();
    });

    it('reports a failed load instead of showing items from earlier arguments', () => {
        renderList({ isError: true, currentData: undefined });

        expect(screen.queryByText('Sales Analytics')).not.toBeInTheDocument();
        expect(screen.getByText("Couldn't load Output Ports")).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument();
    });
});
