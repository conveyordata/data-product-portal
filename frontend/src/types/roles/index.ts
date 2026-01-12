import type {
    DataProductRoleAssignmentResponse,
    GlobalRoleAssignmentResponse,
    OutputPortRoleAssignmentResponse,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';

export type DataProductRoleAssignment = DataProductRoleAssignmentResponse;
export type GlobalRoleAssignment = GlobalRoleAssignmentResponse;
export type OutputPortRoleAssignment = OutputPortRoleAssignmentResponse;

export { DecisionStatus, Prototype, Scope } from './enums.ts';
