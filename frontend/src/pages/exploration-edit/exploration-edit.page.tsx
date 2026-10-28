import { useNavigate, useParams } from 'react-router';
import { ExplorationForm } from '@/components/explorations/exploration-form/exploration-form.component.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

export function ExplorationEdit() {
    const { explorationId } = useParams();
    const navigate = useNavigate();

    if (!explorationId) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    return <ExplorationForm explorationId={explorationId} />;
}
