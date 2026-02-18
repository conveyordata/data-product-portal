import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { createOutputPortPath } from '@/types/navigation';
import { type PendingAction, PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { getRequestLink } from '../../utils/request-utils';

type Props = {
    action: PendingAction;
    outputPortName: string;
};

export function AccessRequestedCell({ action, outputPortName }: Props) {
    const { t } = useTranslation();
    const link = getRequestLink(action);

    if (action.pending_action_type === PendingActionTypes.DataProductDataset) {
        return (
            <div>
                {t('Read access to ')}{' '}
                {link?.datasetId && (
                    <Link to={createOutputPortPath(link.dataProductId, link.datasetId)} style={{ color: '#1890ff' }}>
                        {outputPortName}
                    </Link>
                )}
            </div>
        );
    }

    if (action.pending_action_type === PendingActionTypes.DataProductRoleAssignment) {
        const roleName = action.role ? action.role.name : '';
        return (
            <div>
                {roleName} {t('role')}
            </div>
        );
    }

    if (action.pending_action_type === PendingActionTypes.DatasetRoleAssignment) {
        const roleName = action.role ? action.role.name : '';
        return (
            <div>
                {roleName} {t('role on')}{' '}
                {link?.datasetId && (
                    <Link to={createOutputPortPath(link.dataProductId, link.datasetId)} style={{ color: '#1890ff' }}>
                        {outputPortName}
                    </Link>
                )}
            </div>
        );
    }

    // DataOutputDataset
    if (link?.datasetId) {
        return (
            <Link to={createOutputPortPath(link.dataProductId, link.datasetId)} style={{ color: '#1890ff' }}>
                {outputPortName}
            </Link>
        );
    }

    return <div>{outputPortName}</div>;
}
