import type { DecisionStatus as ApiDecisionStatus } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type {
    Prototype as ApiPrototype,
    Scope as ApiScope,
} from '@/store/api/services/generated/authorizationRolesApi.ts';

export const Prototype = {
    CUSTOM: 0 as ApiPrototype,
    EVERYONE: 1 as ApiPrototype,
    OWNER: 2 as ApiPrototype,
    ADMIN: 3 as ApiPrototype,
} as const;

export type Prototype = (typeof Prototype)[keyof typeof Prototype];

export const Scope = {
    GLOBAL: 'global' as ApiScope,
    DATA_PRODUCT: 'data_product' as ApiScope,
    DATASET: 'dataset' as ApiScope,
};

export type Scope = (typeof Scope)[keyof typeof Scope];

export const DecisionStatus = {
    Approved: 'approved' as ApiDecisionStatus,
    Pending: 'pending' as ApiDecisionStatus,
    Denied: 'denied' as ApiDecisionStatus,
} as const;

export type DecisionStatus = (typeof DecisionStatus)[keyof typeof DecisionStatus];
