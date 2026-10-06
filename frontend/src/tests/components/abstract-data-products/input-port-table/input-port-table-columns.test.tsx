import type { TFunction } from 'i18next';
import type { ReactNode } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { getDataProductDatasetsColumns } from '@/components/abstract-data-products/input-port-tab/components/input-port-table/input-port-table-columns.tsx';
import {
    type AbstractDataProductInputPort as InputPort,
    InputPortStatus,
    OutputPortAccessFunction,
    OutputPortStatus,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

function renderNameCell(accessFunction: OutputPortAccessFunction) {
    const inputPort = {
        status: InputPortStatus.Approved,
        output_port: {
            id: 'output-port-1',
            name: 'Test Output Port',
            namespace: 'test',
            description: '',
            status: OutputPortStatus.Active,
            access_type: { id: 'access-type-1', name: 'Access type', access_function: accessFunction },
            data_product_id: 'dp-1',
            tags: [],
            access_modes: [],
        },
    } as unknown as InputPort;
    const [, nameColumn] = getDataProductDatasetsColumns({
        t: ((key: string) => key) as TFunction,
        canRemoveAccess: false,
        canRequestAccess: false,
        handleCancel: vi.fn(),
        handleRevoke: vi.fn(),
        handleRenew: vi.fn(),
        inputPorts: [inputPort],
    });
    const render = (nameColumn as { render: (value: unknown, record: InputPort, index: number) => ReactNode }).render;
    renderWithProviders(<>{render(undefined, inputPort, 0)}</>, { routerProps: {} });
}

describe('getDataProductDatasetsColumns', () => {
    it('links to a non private output port', () => {
        renderNameCell(OutputPortAccessFunction.Restricted);
        expect(screen.getByRole('link')).toBeInTheDocument();
    });

    it('does not link to a private output port', () => {
        renderNameCell(OutputPortAccessFunction.Private);
        expect(screen.queryByRole('link')).not.toBeInTheDocument();
    });
});
