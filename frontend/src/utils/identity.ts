import type {
    GroupIdentity,
    MachineUserIdentity,
    UserIdentity,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

export type Identity = UserIdentity | GroupIdentity | MachineUserIdentity;

export const IDENTITY_TYPES: Identity['type'][] = ['user', 'group', 'machine_user'];

const sorter = new Sorter<Identity>();
export const compareIdentities = sorter.cascadedSorter(
    sorter.stringSorter((identity) => (identity.type === 'user' ? identity.last_name : identity.display_name)),
    sorter.stringSorter((identity) => (identity.type === 'user' ? identity.first_name : undefined)),
);

export function isUserIdentity(identity: Identity): identity is UserIdentity {
    return identity.type === 'user';
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
    const value = searchTerm.trim().toLowerCase();

    return (
        getIdentityDisplayName(identity).toLowerCase().includes(value) ||
        getIdentitySecondaryLabel(identity).toLowerCase().includes(value) ||
        identity.external_id.toLowerCase().includes(value)
    );
}
