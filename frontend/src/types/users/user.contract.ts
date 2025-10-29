import type { GlobalRoleAssignmentContract } from '../roles/role.contract';

export interface UserContract {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
    has_seen_tour: boolean;
}

export type UsersGetContract = Array<
    UserContract & {
        global_role: GlobalRoleAssignmentContract;
    }
>;
