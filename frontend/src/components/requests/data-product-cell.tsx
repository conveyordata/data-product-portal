import { Link } from 'react-router';
import { createDataProductIdPath } from '@/types/navigation';
import type { PendingAction } from '@/types/pending-actions/pending-actions';
import { getRequestLink } from '../../utils/request-utils';

type Props = {
    action: PendingAction;
    dataProductName: string;
};

export function DataProductCell({ action, dataProductName }: Props) {
    const link = getRequestLink(action);

    if (!link) {
        return <div>{dataProductName}</div>;
    }

    return <Link to={createDataProductIdPath(link.dataProductId)}>{dataProductName}</Link>;
}
