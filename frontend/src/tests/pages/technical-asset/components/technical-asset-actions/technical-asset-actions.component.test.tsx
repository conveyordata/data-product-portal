import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';

import { TechnicalAssetActions } from '@/pages/technical-asset/components/technical-asset-actions/technical-asset-actions.component.tsx';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

const dataProductId = 'data-product-1';
const dataOutputId = 'data-output-1';

describe('TechnicalAssetActions', () => {
    it('renders no tiles', async () => {
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
            http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })),
        );

        renderWithProviders(<TechnicalAssetActions dataProductId={dataProductId} dataOutputId={dataOutputId} />);

        expect(screen.queryByRole('radio')).not.toBeInTheDocument();
    });
});
