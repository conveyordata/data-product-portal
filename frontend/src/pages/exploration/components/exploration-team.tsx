import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';

type Props = {
    explorationId: string;
};
export const ExplorationTeam = ({explorationId}: Props) => {
    const user = useSelector(selectCurrentUser);
    const { data: roleAssignments, isFetching } = useListExploration({
        dataProductId: explorationId,
    });

    return user?.email;
};