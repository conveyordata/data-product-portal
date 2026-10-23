import { beforeEach, describe, expect, it } from 'vitest';
import { DataProductDescription } from '@/pages/data-product/components/data-product-description/data-product-description.tsx';
import { OutputPortDescription } from '@/pages/output-port/components/dataset-description/output-port-description.tsx';
import { TechnicalAssetDescription } from '@/pages/technical-asset/components/technical-asset-description/technical-asset-description.tsx';
import { TechnicalAssetStatus } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { mockEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { mockDataProducts } from '@/tests/mocks/dataProducts.ts';
import { mockGetPlugins } from '@/tests/mocks/plugins.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

const product = {
    ...mockDataProducts[0],
    about: '',
    environments: [
        { environment_id: 'env-tst', environment: mockEnvironments[2], creation_date: '2026-10-12T10:00:00' },
    ],
};

const common = { description: 'Description', tags: [], namespace: 'namespace' };

describe('Read-only inherited environments', () => {
    beforeEach(() => mockGetPlugins());

    it.each([
        [
            'Data Product',
            <DataProductDescription
                key="data-product"
                {...common}
                lifecycle={null}
                type="Reporting"
                domain="Finance"
                environments={product.environments}
            />,
        ],
        [
            'Output Port',
            <OutputPortDescription
                key="output-port"
                {...common}
                lifecycle={null}
                domain="Finance"
                data_product={product}
            />,
        ],
        [
            'Technical Asset',
            <TechnicalAssetDescription
                key="technical-asset"
                {...common}
                status={TechnicalAssetStatus.Active}
                type="S3TechnicalAssetConfiguration"
                accessModes={[]}
                environments={product.environments}
            />,
        ],
    ] as const)('shows declared environments without a picker on %s', (_name, element) => {
        renderWithProviders(element, { routerProps: { initialEntries: ['/'] } });
        expect(screen.getByText('Environments')).toBeInTheDocument();
        expect(screen.getByText('Test')).toBeInTheDocument();
        expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
        expect(screen.queryByLabelText('close')).not.toBeInTheDocument();
    });
});
