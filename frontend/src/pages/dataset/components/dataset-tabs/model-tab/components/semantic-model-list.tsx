import type { SemanticModelResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { SemanticModelCard } from './semantic-model-card';

type Props = {
    models: SemanticModelResponse[];
};

export function SemanticModelList({ models }: Props) {
    return (
        <>
            {models.map((model) => (
                <SemanticModelCard key={model.id} model={model} />
            ))}
        </>
    );
}
