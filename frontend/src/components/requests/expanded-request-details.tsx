import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-actions';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';

type Props = {
    action: PendingAction;
};

function getExpansionContent(action: PendingAction, t: (key: string, params?: Record<string, string>) => string) {
    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return {
            justification: action.justification,
            message: t(
                'Accepting will grant the Data Product {{dataProductName}} read access on the {{outputPortName}}.',
                {
                    dataProductName: action.data_product.name,
                    outputPortName: action.output_port.name,
                },
            ),
            showJustification: true,
        };
    }

    if (action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort) {
        return {
            justification: '',
            message: t('Accepting will grant read access on the {{outputPortName}}.', {
                outputPortName: action.output_port.name,
            }),
            showJustification: false,
        };
    }

    if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
        const roleName = action.role ? action.role.name : t('a role');
        return {
            justification: '',
            message: t(
                'Accepting will grant {{userName}} the {{roleName}} role on the Data Product {{dataProductName}}.',
                {
                    userName: `${action.user.first_name} ${action.user.last_name}`,
                    roleName,
                    dataProductName: action.data_product.name,
                },
            ),
            showJustification: false,
        };
    }
    return {
        justification: '',
        message: '',
        showJustification: false,
    };
}

export function ExpandedRequestDetails({ action }: Props) {
    const { t } = useTranslation();
    const { justification, message, showJustification } = getExpansionContent(action, t);

    return (
        <div style={{ backgroundColor: '#fafafa', padding: '12px 16px' }}>
            {showJustification && (
                <>
                    <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                        {t('BUSINESS JUSTIFICATION')}
                    </Typography.Text>
                    <Typography.Paragraph style={{ marginBottom: 16 }}>
                        {justification || t('No justification provided')}
                    </Typography.Paragraph>
                </>
            )}
            <Typography.Text type="secondary">{message}</Typography.Text>
        </div>
    );
}
