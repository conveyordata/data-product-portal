import { UserContract } from '@/types/users';

export interface DataProductMembershipMemberCreateRequest {
    dataProductId: string;
    user: UserContract;
}
