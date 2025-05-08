export type AccessRequest = {
    action: number;
    resource?: string;
    domain?: string;
};

export type AccessResponse = {
    allowed: boolean;
};
