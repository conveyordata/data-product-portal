import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { createOutputPortPath } from '@/types/navigation';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
} from '@/types/pending-actions/pending-request-types';
import { getRequestLink } from '../../utils/request-utils';

type Props = {
    action: PendingAction;
    outputPortName: string;
};

export function AccessRequestedCell({ action, outputPortName }: Props) {
    const { t } = useTranslation();
    const link = getRequestLink(action);

    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return (
            <div>
                {t('Read access to ')}{' '}
                {link?.datasetId && (
                    <Link to={createOutputPortPath(link.dataProductId, link.datasetId)}>{outputPortName}</Link>
                )}
            </div>
        );
    }

    if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
        const roleName = action.role ? action.role.name : '';
        return (
            <div>
                {roleName} {t('role')}
            </div>
        );
    }

    // DataOutputDataset
    if (link?.datasetId) {
        return <Link to={createOutputPortPath(link.dataProductId, link.datasetId)}>{outputPortName}</Link>;
    }

    return <div>{outputPortName}</div>;
}
