import type { UserContract } from '@/types/users/user.contract.ts';

export type UserCreateRequest = Pick<UserContract, 'email' | 'external_id' | 'first_name' | 'last_name'>;

export type UserCreateResponse = UserContract;
