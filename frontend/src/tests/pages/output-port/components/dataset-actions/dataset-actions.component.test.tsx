import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';

import { DatasetActions } from '@/pages/output-port/components/dataset-actions/dataset-actions.component.tsx';
import { mockGetPlatformTiles } from '@/tests/mocks/plugins.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

const datasetId = 'dataset-1';
const dataProductId = 'data-product-1';

describe('DatasetActions', () => {
    it('renders no tiles when the backend has no enabled integrations', async () => {
        mockGetPlatformTiles({ platform_tiles: [] });
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
            http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })),
        );

        renderWithProviders(<DatasetActions datasetId={datasetId} dataProductId={dataProductId} />);

        expect(screen.queryByRole('radio')).not.toBeInTheDocument();
    });

    it('renders the Coder tile when the backend returns it', async () => {
        mockGetPlatformTiles({
            platform_tiles: [
                {
                    label: 'Coder',
                    value: 'coder',
                    icon_name: 'coder-logo.svg',
                    has_environments: false,
                    has_config: true,
                    children: [],
                    show_in_form: false,
                },
            ],
        });
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
            http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })),
        );

        renderWithProviders(<DatasetActions datasetId={datasetId} dataProductId={dataProductId} />);

        expect(await screen.findByText('Coder')).toBeInTheDocument();
    });
});
