import {
    type Request,
    RequestType_DataProductRoleAssignment,
    RequestType_InputPort,
    RequestType_TechnicalAssetOutputPort,
} from '@/types/request-types/request-types.tsx';

export function filterBySearch(requests: Request[], searchTerm: string): Request[] {
    if (!searchTerm) return requests;

    const lowerSearch = searchTerm.toLowerCase();

    return requests.filter((action) => {
        // Check data link requests
        if (
            action.request_type === RequestType_InputPort ||
            action.request_type === RequestType_TechnicalAssetOutputPort
        ) {
            return (
                action.output_port.name.toLowerCase().includes(lowerSearch) ||
                ('consuming_abstract_data_product' in action &&
                    action.consuming_abstract_data_product.name.toLowerCase().includes(lowerSearch)) ||
                ('technical_asset' in action && action.technical_asset.name.toLowerCase().includes(lowerSearch)) ||
                action.requested_by.first_name.toLowerCase().includes(lowerSearch) ||
                action.requested_by.last_name.toLowerCase().includes(lowerSearch) ||
                action.requested_by.email.toLowerCase().includes(lowerSearch)
            );
        }

        // Check role assignment requests
        if (action.request_type === RequestType_DataProductRoleAssignment) {
            return (
                action.user.first_name.toLowerCase().includes(lowerSearch) ||
                action.user.last_name.toLowerCase().includes(lowerSearch) ||
                action.user.email.toLowerCase().includes(lowerSearch) ||
                action.role?.name.toLowerCase().includes(lowerSearch)
            );
        }

        return false;
    });
}
