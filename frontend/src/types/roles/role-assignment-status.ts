export enum DecisionStatus {
    Approved = 'approved',
    Pending = 'pending',
    Denied = 'denied',
}

export type DecisionStatusType = DecisionStatus.Approved | DecisionStatus.Pending | DecisionStatus.Denied;
