import type {
    DataProductRoleAssignmentResponse,
    GroupIdentity,
    MachineUserIdentity,
    UserIdentity,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';

export type Identity = UserIdentity | GroupIdentity | MachineUserIdentity;

export type UserDataProductRoleAssignment = Omit<DataProductRoleAssignmentResponse, 'identity'> & {
    identity: UserIdentity;
};

export function isUserIdentity(identity: Identity): identity is UserIdentity {
    return identity.type === 'user';
}

export function isUserDataProductRoleAssignment(
    assignment: DataProductRoleAssignmentResponse,
): assignment is UserDataProductRoleAssignment {
    return isUserIdentity(assignment.identity);
}

export function getIdentityDisplayName(identity: Identity): string {
    switch (identity.type) {
        case 'user':
            return `${identity.first_name} ${identity.last_name}`;
        case 'group':
        case 'machine_user':
            return identity.display_name;
    }
}

export function getIdentitySecondaryLabel(identity: Identity): string {
    return identity.type === 'user' ? identity.email : identity.external_id;
}

export function getIdentityTypeLabel(identity: Identity, t: (key: string) => string): string {
    switch (identity.type) {
        case 'user':
            return t('User');
        case 'group':
            return t('Group');
        case 'machine_user':
            return t('Machine User');
    }
}

export function identityMatchesSearch(identity: Identity, searchTerm: string): boolean {
    const value = searchTerm.toLowerCase();

    return (
        getIdentityDisplayName(identity).toLowerCase().includes(value) ||
        getIdentitySecondaryLabel(identity).toLowerCase().includes(value)
    );
}
