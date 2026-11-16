import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';

import { DatasetActions } from '@/pages/output-port/components/dataset-actions/dataset-actions.component.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

const datasetId = 'dataset-1';

describe('DatasetActions', () => {
    it('renders no tiles', async () => {
        allowAllAuth();
        server.use(http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })));

        renderWithProviders(<DatasetActions datasetId={datasetId} />);

        expect(screen.queryByRole('radio')).not.toBeInTheDocument();
    });
});
