import { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';

const InternalExplorer = lazy(() => import('@/components/explorer/internal-explorer.tsx'));

type Props = {
    id: string;
    dataProductId?: string;
    type: 'dataset' | 'dataproduct' | 'dataoutput';
};

export function Explorer(props: Props) {
    return (
        <Suspense fallback={<LoadingSpinner />}>
            <InternalExplorer {...props} />
        </Suspense>
    );
}
