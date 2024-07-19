export interface UserContract {
    id: string;
    email: string;
    external_id: string;
    first_name: string;
    last_name: string;
    is_admin: boolean;
}

export interface UserModel extends UserContract {}
