import { describe, expect, it } from 'vitest';
import { OutputPortDescription } from '@/pages/output-port/components/dataset-description/output-port-description.tsx';
import type { GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

function renderDescription(dataProduct?: GetDataProductResponse) {
    renderWithProviders(
        <OutputPortDescription
            lifecycle={null}
            description=""
            data_product={dataProduct}
            domain="Finance"
            tags={[]}
            namespace="output-port"
        />,
        { routerProps: {} },
    );
}

describe('OutputPortDescription', () => {
    it('links to the producing data product when it is readable', () => {
        renderDescription({ id: 'dp-1', name: 'Producer' } as GetDataProductResponse);
        expect(screen.getByRole('link', { name: 'Producer' })).toBeInTheDocument();
    });

    it('omits the data product when it is not readable', () => {
        renderDescription();
        expect(screen.queryByText('Data Product')).not.toBeInTheDocument();
        expect(screen.getByText('Finance')).toBeInTheDocument();
    });
});
