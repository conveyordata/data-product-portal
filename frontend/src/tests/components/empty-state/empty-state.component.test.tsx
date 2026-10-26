import { Button } from 'antd';
import { describe, expect, it, vi } from 'vitest';
import {
    EmptyState,
    type EmptyStateQuery,
    emptyStateQueryProps,
    hasFailed,
    isAwaitingData,
} from '@/components/empty-state/empty-state.component.tsx';
import { renderWithProviders, screen, userEvent } from '../../test-utils';

const baseProps = {
    icon: <span />,
    title: 'No Data Products yet',
    description: 'Create one',
    action: <Button>Create Data Product</Button>,
};

const settledQuery: EmptyStateQuery = {
    isFetching: false,
    isUninitialized: false,
    isError: false,
    currentData: [],
    refetch: vi.fn(),
};

describe('EmptyState', () => {
    it('shows the title, description and action when nothing is filtered', () => {
        renderWithProviders(
            <EmptyState {...baseProps} subject="Data Products" filter={{ searchTerm: '', onClear: vi.fn() }} />,
        );

        expect(screen.getByRole('status')).toHaveTextContent('No Data Products yet');
        expect(screen.getByText('Create one')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Create Data Product' })).toBeInTheDocument();
    });

    it('names the search term and offers to clear it instead of the action', async () => {
        const onClear = vi.fn();
        renderWithProviders(
            <EmptyState {...baseProps} subject="Data Products" filter={{ searchTerm: 'xx', onClear }} />,
        );

        expect(screen.getByText('No Data Products match "xx"')).toBeInTheDocument();
        expect(screen.queryByText('Create one')).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Create Data Product' })).not.toBeInTheDocument();

        await userEvent.click(screen.getByRole('button', { name: 'Clear search' }));
        expect(onClear).toHaveBeenCalledOnce();
    });

    it('mentions the other filters when a search term and a filter are both active', () => {
        renderWithProviders(
            <EmptyState
                {...baseProps}
                subject="Data Products"
                filter={{ searchTerm: 'xx', hasOtherFilters: true, onClear: vi.fn() }}
            />,
        );

        expect(screen.getByText('No Data Products match "xx" with the current filters')).toBeInTheDocument();
    });

    it('treats other active filters without a search term as filtered', () => {
        renderWithProviders(
            <EmptyState {...baseProps} subject="Data Products" filter={{ hasOtherFilters: true, onClear: vi.fn() }} />,
        );

        expect(screen.getByText('No Data Products match the current filters')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Clear filters' })).toBeInTheDocument();
    });

    it('reports a failed load instead of claiming nothing exists, and retries', async () => {
        const refetch = vi.fn();
        renderWithProviders(
            <EmptyState
                {...baseProps}
                subject="Data Products"
                filter={{ searchTerm: 'xx', onClear: vi.fn() }}
                {...emptyStateQueryProps({ ...settledQuery, isError: true, currentData: undefined, refetch })}
            />,
        );

        expect(screen.getByText("Couldn't load Data Products")).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Clear search' })).not.toBeInTheDocument();
        await userEvent.click(screen.getByRole('button', { name: 'Try again' }));
        expect(refetch).toHaveBeenCalledOnce();
    });

    it('treats a failed refetch that still has data as not failed', () => {
        expect(hasFailed({ ...settledQuery, isError: true })).toBe(false);
        expect(hasFailed({ ...settledQuery, isError: true, currentData: undefined })).toBe(true);
    });

    it('awaits data on first load, new arguments or a skipped query, not on a background refetch', () => {
        expect(isAwaitingData({ ...settledQuery, isFetching: true, currentData: undefined })).toBe(true);
        expect(isAwaitingData({ ...settledQuery, isUninitialized: true, currentData: undefined })).toBe(true);
        expect(isAwaitingData({ ...settledQuery, isFetching: true })).toBe(false);
    });

    it('renders nothing while loading', () => {
        renderWithProviders(<EmptyState {...baseProps} loading />);

        expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });
});
