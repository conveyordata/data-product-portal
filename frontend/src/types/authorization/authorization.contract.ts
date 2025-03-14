export type AccessRequest = {
    object_id?: string;
    domain?: string;
    action: number;
};

export type AccessResponse = {
    access: boolean;
};
