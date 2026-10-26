import { describe, expect, it, vi } from 'vitest';
import type { EmptyStateQuery } from '@/components/empty-state/empty-state.component.tsx';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { renderWithProviders, screen, userEvent, within } from '../../test-utils';

type Row = { id: string; domain: string };

const rows: Row[] = [
    { id: '1', domain: 'Sales' },
    { id: '2', domain: 'Marketing' },
];

const columns = [
    {
        title: 'Domain',
        dataIndex: 'domain',
        filters: [
            { text: 'Sales', value: 'Sales' },
            { text: 'Finance', value: 'Finance' },
        ],
        onFilter: (value: unknown, record: Row) => record.domain === value,
    },
];

const settledQuery: EmptyStateQuery = {
    isFetching: false,
    isUninitialized: false,
    isError: false,
    currentData: rows,
    refetch: vi.fn(),
};

function renderTable(query: Partial<EmptyStateQuery> = {}, props: { loading?: boolean; onClear?: () => void } = {}) {
    const onChange = vi.fn();
    const { container } = renderWithProviders(
        <ListTable<Row>
            query={{ ...settledQuery, ...query }}
            dataSource={rows}
            columns={columns}
            subject="Data Products"
            emptyState={{ icon: <span />, title: 'No Data Products yet' }}
            filter={{ onClear: props.onClear ?? vi.fn() }}
            loading={props.loading}
            onChange={onChange}
            rowKey="id"
        />,
    );
    return { container, onChange };
}

describe('ListTable', () => {
    it('reports a failed load instead of showing rows, and retries', async () => {
        const refetch = vi.fn();
        renderTable({ isError: true, currentData: undefined, refetch });

        expect(screen.queryByText('Sales')).not.toBeInTheDocument();
        await userEvent.click(screen.getByRole('button', { name: 'Try again' }));
        expect(refetch).toHaveBeenCalledOnce();
        expect(screen.getByText("Couldn't load Data Products")).toBeInTheDocument();
    });

    it('keeps the rows when a refetch fails but data for the current arguments exists', () => {
        renderTable({ isError: true });

        expect(screen.getByText('Sales')).toBeInTheDocument();
    });

    it('spins only while there is no data for the current arguments, or while extra work runs', () => {
        expect(
            renderTable({ isFetching: true, currentData: undefined }).container.querySelector('.ant-spin-spinning'),
        ).toBeInTheDocument();
        expect(renderTable({ isFetching: true }).container.querySelector('.ant-spin-spinning')).toBeNull();
        expect(renderTable({}, { loading: true }).container.querySelector('.ant-spin-spinning')).toBeInTheDocument();
    });

    it('treats an active column filter as filtered, and clearing resets it', async () => {
        const onClear = vi.fn();
        const { onChange } = renderTable({}, { onClear });

        await userEvent.click(screen.getByRole('button', { name: 'filter' }));
        await userEvent.click(await screen.findByText('Finance'));
        await userEvent.click(screen.getByRole('button', { name: 'OK' }));

        expect(onChange).toHaveBeenCalled();
        const status = await screen.findByRole('status');
        expect(within(status).getByText('No Data Products match the current filters')).toBeInTheDocument();

        await userEvent.click(within(status).getByRole('button', { name: 'Clear filters' }));
        expect(onClear).toHaveBeenCalledOnce();
        expect(await screen.findByRole('cell', { name: 'Sales' })).toBeInTheDocument();
    });
});
