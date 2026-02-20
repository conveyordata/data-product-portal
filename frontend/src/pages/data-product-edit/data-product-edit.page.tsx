import { useNavigate, useParams } from 'react-router';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

export function DataProductEdit() {
    const { dataProductId } = useParams();
    const navigate = useNavigate();

    if (!dataProductId) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    return <DataProductForm dataProductId={dataProductId} mode={'edit'} />;
}
