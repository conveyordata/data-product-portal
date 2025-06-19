import type {
    DataProductRoleAssignmentContract,
    DatasetRoleAssignmentContract,
    GlobalRoleAssignmentContract,
} from '../roles/role.contract';

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
    global_role: GlobalRoleAssignmentContract | null;
    bio?: string;
    created_on: string;
    dataset_roles: DatasetRoleAssignmentContract[];
    data_product_roles: DataProductRoleAssignmentContract[];
}
