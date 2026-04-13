import { useSearchParams } from 'react-router';
import { ConsumerExplorationForm } from '@/components/data-products/consumer-exploration-form/consumer-exploration-form.component.tsx';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';

export function DataProductCreate() {
    const [searchParams] = useSearchParams();

    if (searchParams.get('exploration') === 'true') {
        return <ConsumerExplorationForm mode="create" />;
    }
    return <DataProductForm mode="create" />;
}
