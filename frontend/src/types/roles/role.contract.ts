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
