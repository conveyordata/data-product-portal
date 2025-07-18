import type { DataProductContract } from '../data-product';
import type { DatasetContract } from '../dataset';
import type { UserContract } from '../users';
import type { DecisionStatus } from './role-assignment-status';

export const Prototype = {
    CUSTOM: 0,
    EVERYONE: 1,
    OWNER: 2,
    ADMIN: 3,
} as const;

export type Prototype = (typeof Prototype)[keyof typeof Prototype];

export const Scope = {
    GLOBAL: 'global',
    DATA_PRODUCT: 'data_product',
    DATASET: 'dataset',
};

export type Scope = (typeof Scope)[keyof typeof Scope];

export interface RoleContract {
    id: string;
    name: string;
    scope: Scope;
    description: string;
    permissions: number[];
    prototype: Prototype;
}

export interface RoleUpdate {
    id: string;
    name?: string;
    scope?: Scope;
    description?: string;
    permissions?: number[];
}

export interface DataProductRoleAssignmentCreateContract {
    data_product_id: string;
    user_id: string;
    role_id: string;
}

export interface DataProductRoleAssignmentContract {
    id: string;
    data_product: DataProductContract;
    user: UserContract;
    role: RoleContract;
    decision: DecisionStatus;
    requested_on?: string;
    requested_by?: UserContract;
    decided_on?: string;
    decided_by?: UserContract;
}

export interface DatasetRoleAssignmentCreateContract {
    dataset_id: string;
    user_id: string;
    role_id: string;
}

export interface DatasetRoleAssignmentContract {
    id: string;
    dataset: DatasetContract;
    user: UserContract;
    role: RoleContract;
    decision: DecisionStatus;
    requested_on?: string;
    requested_by?: UserContract;
    decided_on?: string;
    decided_by?: UserContract;
}

export interface GlobalRoleAssignmentContract {
    id: string;
    user: UserContract;
    role: RoleContract;
    decision: DecisionStatus;
    requested_on?: string;
    requested_by?: UserContract;
    decided_on?: string;
    decided_by?: UserContract;
}

export interface GlobalRoleAssignmentCreateContract {
    user_id: string;
    role_id: string;
}
