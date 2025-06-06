import type { BadgeProps } from 'antd';
import type { TFunction } from 'i18next';

import { DataOutputStatus } from '@/types/data-output';
import { DataProductStatus } from '@/types/data-product';
import { DecisionStatus } from '@/types/roles';
import type { Status } from '@/types/shared';

export function getStatusLabel(t: TFunction, status: Status): string {
    switch (status) {
        case DataProductStatus.Pending || DataOutputStatus.Pending:
            return t('Pending');
        case DataProductStatus.Active || DataOutputStatus.Active:
            return t('Active');
        case DataProductStatus.Deleted || DataOutputStatus.Deleted:
            return t('Deleted');
        default:
            return t('Unknown');
    }
}

export function getBadgeStatus(status: Status): BadgeProps['status'] {
    switch (status) {
        case DataProductStatus.Pending || DataOutputStatus.Pending:
            return 'processing';
        case DataProductStatus.Active || DataOutputStatus.Active:
            return 'success';
        case DataProductStatus.Deleted || DataOutputStatus.Deleted:
            return 'error';
        default:
            return 'default';
    }
}

export function getDecisionStatusLabel(t: TFunction, status: DecisionStatus): string {
    switch (status) {
        case DecisionStatus.Pending:
            return t('Requested');
        case DecisionStatus.Approved:
            return t('Available');
        case DecisionStatus.Denied:
            return t('Rejected');
        default:
            return t('Unknown');
    }
}

export function getDecisionStatusBadgeStatus(status: DecisionStatus): BadgeProps['status'] {
    switch (status) {
        case DecisionStatus.Pending:
            return 'processing';
        case DecisionStatus.Approved:
            return 'success';
        case DecisionStatus.Denied:
            return 'error';
        default:
            return 'default';
    }
}

export function getRoleAssignmentBadgeStatus(status: DecisionStatus): BadgeProps['status'] {
    switch (status) {
        case DecisionStatus.Approved:
            return 'success';
        case DecisionStatus.Denied:
            return 'default';
        default:
            return 'processing';
    }
}

export function getRoleAssignmentStatusLabel(t: TFunction, role: DecisionStatus): string {
    switch (role) {
        case DecisionStatus.Approved:
            return t('Approved');
        case DecisionStatus.Denied:
            return t('Denied');
        default:
            return t('Pending');
    }
}
