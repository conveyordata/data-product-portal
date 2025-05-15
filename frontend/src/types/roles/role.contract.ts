import { DataProductContract } from '../data-product';
import { UserContract } from '../users';
import { DecisionStatus } from './role-assignment-status';

export const Prototype = {
    CUSTOM: 0,
    EVERYONE: 1,
    OWNER: 2,
    ADMIN: 3,
} as const;

export type Prototype = (typeof Prototype)[keyof typeof Prototype];

export interface RoleContract {
    id: string;
    name: string;
    scope: string;
    description: string;
    permissions: number[];
    prototype: Prototype;
}

export interface RoleUpdate {
    id: string;
    name?: string;
    scope?: string;
    description?: string;
    permissions?: number[];
}

export interface RoleAssignmentCreateContract {
    data_product_id: string;
    user_id: string;
    role_id: string;
}

export interface RoleAssignmentContract {
    id: string;
    data_product: DataProductContract;
    user: UserContract;
    role: RoleContract;
    decision: DecisionStatus;
    requested_on: string | null;
    requested_by: UserContract | null;
    decided_on: string | null;
    decided_by: UserContract | null;
}
