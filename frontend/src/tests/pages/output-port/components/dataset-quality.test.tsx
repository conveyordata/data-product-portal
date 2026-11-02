import { delay, HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { DatasetQuality } from '@/pages/output-port/components/dataset-quality/dataset-quality.component.tsx';
import {
    DataQualityStatus,
    useGetLatestDataQualitySummaryForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsDataQualityApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

function Refetch() {
    const { refetch, isFetching } = useGetLatestDataQualitySummaryForOutputPortQuery({
        dataProductId: 'dp1',
        id: 'op1',
    });
    return (
        <button type="button" onClick={refetch}>
            {isFetching ? 'Refetching' : 'Refetch'}
        </button>
    );
}

describe('DatasetQuality', () => {
    it('does not keep the previous output port quality when the next one has none', async () => {
        server.use(
            http.get('*/api/v2/data_products/dp1/output_ports/with-quality/data_quality_summary', () =>
                HttpResponse.json({
                    id: 'summary1',
                    output_port_id: 'with-quality',
                    created_at: new Date().toISOString(),
                    overall_status: DataQualityStatus.Success,
                    technical_assets: [],
                }),
            ),
            http.get('*/api/v2/data_products/dp1/output_ports/without-quality/data_quality_summary', () =>
                HttpResponse.json({ detail: 'Not found' }, { status: 404 }),
            ),
        );

        const { rerender } = renderWithProviders(<DatasetQuality dataProductId="dp1" datasetId="with-quality" />);
        expect(await screen.findByText('Passed')).toBeInTheDocument();

        rerender(<DatasetQuality dataProductId="dp1" datasetId="without-quality" />);

        expect(await screen.findByText('Ask the owners to publish data quality information')).toBeInTheDocument();
        expect(screen.getByText('No data')).toBeInTheDocument();
        expect(screen.queryByText('Passed')).not.toBeInTheDocument();
    });

    it('keeps showing the quality while it refetches', async () => {
        let requests = 0;
        server.use(
            http.get('*/api/v2/data_products/dp1/output_ports/op1/data_quality_summary', async () => {
                requests++;
                if (requests > 1) await delay(100);
                return HttpResponse.json({
                    id: 'summary1',
                    output_port_id: 'op1',
                    created_at: new Date().toISOString(),
                    overall_status: DataQualityStatus.Success,
                    technical_assets: [],
                });
            }),
        );

        renderWithProviders(
            <>
                <DatasetQuality dataProductId="dp1" datasetId="op1" />
                <Refetch />
            </>,
        );
        expect(await screen.findByText('Passed')).toBeInTheDocument();

        await userEvent.click(screen.getByRole('button', { name: 'Refetch' }));

        expect(await screen.findByText('Refetching')).toBeInTheDocument();
        expect(screen.getByText('Passed')).toBeInTheDocument();
    });
});
