import { Table } from 'antd';
import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { DatasetQuality } from '@/pages/output-port/components/dataset-quality/dataset-quality.component.tsx';
import { getOutputPortTableColumns } from '@/pages/product-studio/components/output-ports-tab/output-ports-table-columns.tsx';
import { DataQualityStatus } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import i18n from '@/tests/i18n';
import { mockOutputPorts } from '@/tests/mocks/outputPortsSearch.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, waitFor, within } from '@/tests/test-utils.tsx';

describe('Output Port quality status', () => {
    it.each([
        [DataQualityStatus.Success, 'Passed', 'success'],
        [DataQualityStatus.Failure, 'Failed', 'error'],
        [DataQualityStatus.Warning, 'Warning', 'warning'],
        [DataQualityStatus.Error, 'Error', 'error'],
        [DataQualityStatus.Unknown, 'Unknown', 'default'],
    ])('shows the same badge in the table and detail view for %s', async (status, label, color) => {
        const outputPort = { ...mockOutputPorts[0], quality_status: status };
        server.use(
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:id/data_quality_summary', () =>
                HttpResponse.json({
                    overall_status: status,
                    created_at: '2026-01-01T00:00:00Z',
                }),
            ),
        );

        renderWithProviders(
            <>
                <Table
                    columns={getOutputPortTableColumns({ t: i18n.t, outputPorts: [outputPort] })}
                    dataSource={[outputPort]}
                    rowKey="id"
                    pagination={false}
                />
                <DatasetQuality dataProductId={outputPort.data_product_id} datasetId={outputPort.id} />
            </>,
        );

        await waitFor(() => expect(screen.getAllByText(label)).toHaveLength(2));
        const badges = screen.getAllByText(label);
        expect(badges).toHaveLength(2);
        for (const badge of badges) {
            expect(badge.closest('.ant-tag')).toHaveClass(`ant-tag-${color}`);
        }
    });

    it('shows Unknown in the table when no quality summary exists', () => {
        const outputPort = { ...mockOutputPorts[0], quality_status: null };
        renderWithProviders(
            <Table
                columns={getOutputPortTableColumns({ t: i18n.t, outputPorts: [outputPort] })}
                dataSource={[outputPort]}
                rowKey="id"
                pagination={false}
            />,
        );

        expect(within(screen.getByRole('table')).getByText('Unknown')).toBeInTheDocument();
    });
});
