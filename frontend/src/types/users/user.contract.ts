import type { GlobalRoleAssignmentContract } from '../roles/role.contract';

export interface UserContract {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
}

export type UsersGetContract = Array<
    UserContract & {
        global_role: GlobalRoleAssignmentContract;
    }
>;

export interface UserResponseContract extends UserContract {
    phone?: string;
    location?: string;
    joinDate: string;
    global_role: GlobalRoleAssignmentContract | null;
    dataProducts?: number;
    tags?: string[];
    description?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    last_login?: string;
    is_deleted?: boolean;
    is_pending?: boolean;
}
