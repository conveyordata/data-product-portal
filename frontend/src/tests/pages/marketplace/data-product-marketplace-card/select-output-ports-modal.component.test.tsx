import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SelectOutputPortsModal } from '@/pages/marketplace/data-product-marketplace-card/select-output-ports-modal.component.tsx';
import {
    DataProductIconKey,
    type SearchDataProductsResponseItem,
} from '@/store/api/services/generated/dataProductsSearchApi.ts';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

const dataProduct: SearchDataProductsResponseItem = {
    id: 'dp-1',
    name: 'Marketing Campaign Analysis',
    description: 'Campaign KPIs',
    tags: [],
    domain: { id: 'dom-1', name: 'Customer Insights', namespace: 'ci', description: '' },
    type: { id: 'type-1', name: 'Analytics', description: '', icon_key: DataProductIconKey.Analytics },
    lifecycle: null,
    output_ports: [
        {
            id: 'op-1',
            name: 'Campaign Performance Summary',
            description: 'Daily KPIs per campaign',
            access_modes: [
                { id: 'read', name: 'Read', description: '' },
                { id: 'write', name: 'Write', description: '' },
            ],
        },
        { id: 'op-2', name: 'Ad Spend vs ROI', description: 'Spend compared with results', access_modes: [] },
    ],
    consumer_count: 0,
};

function cart() {
    return JSON.parse(localStorage.getItem('CartOutputPortIds') ?? '[]');
}

describe('SelectOutputPortsModal', () => {
    beforeEach(() => localStorage.clear());

    it('adds the checked Output Ports with their access mode', async () => {
        const onClose = vi.fn();
        const user = userEvent.setup();
        renderWithProviders(<SelectOutputPortsModal dataProduct={dataProduct} onClose={onClose} />, {
            routerProps: { initialEntries: ['/marketplace'] },
        });

        await user.click(screen.getByLabelText('Campaign Performance Summary'));
        await user.click(screen.getByText('Add 1 to cart'));

        expect(cart()).toEqual([{ outputPortId: 'op-1', accessModeId: 'read' }]);
        expect(onClose).toHaveBeenCalled();
    });

    it('adds an Output Port with the chosen access mode', async () => {
        const user = userEvent.setup();
        renderWithProviders(<SelectOutputPortsModal dataProduct={dataProduct} onClose={vi.fn()} />, {
            routerProps: { initialEntries: ['/marketplace'] },
        });

        await user.click(screen.getByLabelText('Campaign Performance Summary'));
        await user.click(screen.getByLabelText('Access mode for Campaign Performance Summary'));
        await user.click(await screen.findByText('Write'));
        await user.click(screen.getByText('Add 1 to cart'));

        expect(cart()).toEqual([{ outputPortId: 'op-1', accessModeId: 'write' }]);
    });

    it('changes the access mode of an Output Port already in the cart', async () => {
        const user = userEvent.setup();
        renderWithProviders(<SelectOutputPortsModal dataProduct={dataProduct} onClose={vi.fn()} />, {
            routerProps: { initialEntries: ['/marketplace'] },
            preloadedState: { cart: { DatasetIds: ['op-1'] } },
        });

        await user.click(screen.getByLabelText('Access mode for Campaign Performance Summary'));
        await user.click(await screen.findByText('Write'));
        await user.click(screen.getByText('Update cart'));

        expect(cart()).toEqual([{ outputPortId: 'op-1', accessModeId: 'write' }]);
    });

    it('checks a single Output Port for the user', () => {
        renderWithProviders(
            <SelectOutputPortsModal
                dataProduct={{ ...dataProduct, output_ports: [dataProduct.output_ports[0]] }}
                onClose={vi.fn()}
            />,
            { routerProps: { initialEntries: ['/marketplace'] } },
        );

        expect(screen.getByLabelText('Campaign Performance Summary')).toBeChecked();
        expect(screen.getByText('Add 1 to cart').closest('button')).toBeEnabled();
    });

    it('disables adding when nothing is checked', () => {
        renderWithProviders(<SelectOutputPortsModal dataProduct={dataProduct} onClose={vi.fn()} />, {
            routerProps: { initialEntries: ['/marketplace'] },
        });

        expect(screen.getByText('Add 0 to cart').closest('button')).toBeDisabled();
    });

    it('checks Output Ports already in the cart and removes unchecked ones', async () => {
        const user = userEvent.setup();
        renderWithProviders(<SelectOutputPortsModal dataProduct={dataProduct} onClose={vi.fn()} />, {
            routerProps: { initialEntries: ['/marketplace'] },
            preloadedState: { cart: { DatasetIds: ['op-2'] } },
        });

        const inCart = screen.getByLabelText('Ad Spend vs ROI');
        expect(inCart).toBeChecked();

        await user.click(inCart);
        await user.click(screen.getByText('Update cart'));

        expect(cart()).toEqual([]);
    });
});
