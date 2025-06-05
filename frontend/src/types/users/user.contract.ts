import { GlobalRoleAssignmentContract } from '../roles/role.contract';

export interface UserContract {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
}

export type UsersGetContract = Array<
    UserContract & {
        global_roles: GlobalRoleAssignmentContract[];
    }
>;
