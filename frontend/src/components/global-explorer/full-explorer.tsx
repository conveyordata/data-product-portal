import { ReactFlowProvider } from '@xyflow/react';
import { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';

const InternalFullExplorer = lazy(() => import('@/components/global-explorer/internal-explorer.tsx'));

export function FullExplorer() {
    return (
        <ReactFlowProvider>
            <Suspense fallback={<LoadingSpinner />}>
                <InternalFullExplorer />
            </Suspense>
        </ReactFlowProvider>
    );
}
