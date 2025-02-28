export interface RoleContract {
    id: string;
    name: string;
    scope: string;
    description: string;
    permissions: number[];
}
