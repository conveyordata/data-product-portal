export const DecisionStatus = {
    Approved: 'approved',
    Pending: 'pending',
    Denied: 'denied',
} as const;
export type DecisionStatus = (typeof DecisionStatus)[keyof typeof DecisionStatus];
