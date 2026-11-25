import { afterEach, describe, expect, it, vi } from 'vitest';
import { useGridColumnCount } from '@/pages/marketplace/use-grid-column-count.tsx';
import { stubResizeObserver } from '@/tests/mocks/resizeObserver.ts';
import { act, render, screen } from '@/tests/test-utils.tsx';

function Grid() {
    const { ref, columns } = useGridColumnCount(360, 12, 4);
    return <div ref={ref}>{columns}</div>;
}

describe('useGridColumnCount', () => {
    afterEach(() => vi.unstubAllGlobals());

    it('uses the fallback until the grid is measured', () => {
        render(<Grid />);

        expect(screen.getByText('4')).toBeInTheDocument();
    });

    it('fits as many columns as the measured width allows', () => {
        const reportWidth = stubResizeObserver();
        render(<Grid />);

        act(() => reportWidth(1500));

        expect(screen.getByText('4')).toBeInTheDocument();

        act(() => reportWidth(1100));

        expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('keeps at least one column on a narrow screen', () => {
        const reportWidth = stubResizeObserver();
        render(<Grid />);

        act(() => reportWidth(200));

        expect(screen.getByText('1')).toBeInTheDocument();
    });
});
