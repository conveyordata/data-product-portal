import { describe, expect, it } from 'vitest';
import { QualityBadge } from '@/components/quality-badge/quality-badge.component.tsx';
import { DataQualityStatus } from '@/store/api/services/generated/dataProductsOutputPortsDataQualityApi.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

describe('QualityBadge', () => {
    it.each([undefined, null])('shows No data when there is no status (%o)', (status) => {
        renderWithProviders(<QualityBadge status={status} />);

        expect(screen.getByText('No data')).toBeInTheDocument();
        expect(screen.queryByText('Unknown')).not.toBeInTheDocument();
    });

    it('shows Unknown for a reported unknown status', () => {
        renderWithProviders(<QualityBadge status={DataQualityStatus.Unknown} />);

        expect(screen.getByText('Unknown')).toBeInTheDocument();
        expect(screen.queryByText('No data')).not.toBeInTheDocument();
    });

    it('links to the details when a details URL is given', () => {
        renderWithProviders(
            <QualityBadge
                status={DataQualityStatus.Success}
                createdAt={new Date().toISOString()}
                detailsUrl="https://ci.example.com/run/1"
            />,
        );

        expect(screen.getByRole('link')).toHaveAttribute('href', 'https://ci.example.com/run/1');
    });

    it('is not a link without a details URL', () => {
        const { container } = renderWithProviders(
            <QualityBadge status={DataQualityStatus.Success} createdAt={new Date().toISOString()} />,
        );

        expect(screen.getByText('Passed')).toBeInTheDocument();
        expect(container.querySelector('a')).not.toBeInTheDocument();
    });
});
