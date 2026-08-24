import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';

import { DatasetActions } from '@/pages/output-port/components/dataset-actions/dataset-actions.component.tsx';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

const datasetId = 'dataset-1';

describe('DatasetActions', () => {
    it('renders no tiles', async () => {
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
            http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })),
        );

        renderWithProviders(<DatasetActions datasetId={datasetId} />);

        expect(screen.queryByRole('radio')).not.toBeInTheDocument();
    });
});
