import { beforeEach, describe, expect, it } from 'vitest';
import { DataProductMarketplaceCard } from '@/pages/marketplace/data-product-marketplace-card/data-product-marketplace-card.component.tsx';
import {
    DataProductIconKey,
    type SearchDataProductsOutputPort,
    type SearchDataProductsResponseItem,
} from '@/store/api/services/generated/dataProductsSearchApi.ts';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

const read = { id: 'read', name: 'Read', description: 'Read access' };
const write = { id: 'write', name: 'Write', description: 'Write access' };

function outputPort(id: string, access_modes = [read]): SearchDataProductsOutputPort {
    return { id, name: `Output Port ${id}`, description: `Description ${id}`, access_modes };
}

function dataProduct(output_ports: SearchDataProductsOutputPort[]): SearchDataProductsResponseItem {
    return {
        id: 'dp-1',
        name: 'Marketing Campaign Analysis',
        description: 'Campaign KPIs',
        tags: [],
        domain: { id: 'dom-1', name: 'Customer Insights', namespace: 'ci', description: '' },
        type: { id: 'type-1', name: 'Analytics', description: '', icon_key: DataProductIconKey.Analytics },
        lifecycle: null,
        output_ports,
        consumer_count: 2,
    };
}

function cart() {
    return JSON.parse(localStorage.getItem('CartOutputPortIds') ?? '[]');
}

function renderCard(item: SearchDataProductsResponseItem) {
    renderWithProviders(<DataProductMarketplaceCard dataProduct={item} />, {
        routerProps: { initialEntries: ['/marketplace'] },
    });
}

describe('DataProductMarketplaceCard', () => {
    beforeEach(() => localStorage.clear());

    it('disables adding to the cart when the Data Product has no Output Ports', () => {
        renderCard(dataProduct([]));

        expect(screen.getByText('Add to cart').closest('button')).toBeDisabled();
    });

    it('adds a single Output Port with one access mode directly to the cart', async () => {
        const user = userEvent.setup();
        renderCard(dataProduct([outputPort('op-1')]));

        await user.click(screen.getByText('Add to cart'));

        expect(screen.getByText('In cart')).toBeInTheDocument();
        expect(cart()).toEqual([{ outputPortId: 'op-1', accessModeId: 'read' }]);
    });

    it('adds a single Output Port without access modes directly to the cart', async () => {
        const user = userEvent.setup();
        renderCard(dataProduct([outputPort('op-1', [])]));

        await user.click(screen.getByText('Add to cart'));

        expect(cart()).toEqual([{ outputPortId: 'op-1' }]);
    });

    it('removes a directly added Output Port when clicked again', async () => {
        const user = userEvent.setup();
        renderCard(dataProduct([outputPort('op-1')]));

        await user.click(screen.getByText('Add to cart'));
        await user.click(screen.getByText('In cart'));

        expect(cart()).toEqual([]);
    });

    it('shows how many Output Ports are in the cart when only some are', () => {
        renderWithProviders(
            <DataProductMarketplaceCard dataProduct={dataProduct([outputPort('op-1'), outputPort('op-2')])} />,
            {
                routerProps: { initialEntries: ['/marketplace'] },
                preloadedState: { cart: { DatasetIds: ['op-2'] } },
            },
        );

        expect(screen.getByText('1 of 2 in cart')).toBeInTheDocument();
    });

    it('shows the Data Product is in the cart when all its Output Ports are', () => {
        renderWithProviders(
            <DataProductMarketplaceCard dataProduct={dataProduct([outputPort('op-1'), outputPort('op-2')])} />,
            {
                routerProps: { initialEntries: ['/marketplace'] },
                preloadedState: { cart: { DatasetIds: ['op-1', 'op-2'] } },
            },
        );

        expect(screen.getByText('In cart')).toBeInTheDocument();
    });

    it('opens the selection modal for several Output Ports', async () => {
        const user = userEvent.setup();
        renderCard(dataProduct([outputPort('op-1'), outputPort('op-2')]));

        await user.click(screen.getByText('Add to cart'));

        expect(
            await screen.findByText('Select the Output Ports you need and pick an access mode for each.'),
        ).toBeInTheDocument();
        expect(cart()).toEqual([]);
    });

    it('opens the selection modal for one Output Port with several access modes', async () => {
        const user = userEvent.setup();
        renderCard(dataProduct([outputPort('op-1', [read, write])]));

        await user.click(screen.getByText('Add to cart'));

        expect(
            await screen.findByText('Select the Output Ports you need and pick an access mode for each.'),
        ).toBeInTheDocument();
    });

    it('keeps the chosen access mode when the selection is opened again', async () => {
        const user = userEvent.setup();
        renderCard(dataProduct([outputPort('op-1', [read, write]), outputPort('op-2')]));

        await user.click(screen.getByText('Add to cart'));
        await user.click(screen.getByLabelText('Output Port op-1'));
        await user.click(screen.getByLabelText('Access mode for Output Port op-1'));
        await user.click(await screen.findByText('Write'));
        await user.click(screen.getByText('Add 1 to cart'));

        await user.click(screen.getByText('1 of 2 in cart'));
        await user.click(await screen.findByText('Update cart'));

        expect(cart()).toEqual([{ outputPortId: 'op-1', accessModeId: 'write' }]);
    });
});
