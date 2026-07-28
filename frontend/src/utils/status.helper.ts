import type { BadgeProps } from 'antd';
import type { TFunction } from 'i18next';
import {
    AbstractDataProductStatus,
    InputPortStatus,
    TechnicalAssetStatus,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { OutputPortStatus } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { DecisionStatus, InputPortRequestDecision } from '@/types/roles';

export function getStatusLabel(
    t: TFunction,
    status: TechnicalAssetStatus | AbstractDataProductStatus | OutputPortStatus,
): string {
    switch (status) {
        case AbstractDataProductStatus.Pending || TechnicalAssetStatus.Pending || OutputPortStatus.Pending:
            return t('Pending');
        case AbstractDataProductStatus.Active || TechnicalAssetStatus.Active || OutputPortStatus.Active:
            return t('Active');
        case AbstractDataProductStatus.Archived || TechnicalAssetStatus.Archived || OutputPortStatus.Archived:
            return t('Deleted');
        case AbstractDataProductStatus.Deleting:
            return t('Deleting');
        default:
            return t('Unknown');
    }
}

export function getBadgeStatus(
    status: TechnicalAssetStatus | AbstractDataProductStatus | OutputPortStatus,
): BadgeProps['status'] {
    switch (status) {
        case AbstractDataProductStatus.Pending || TechnicalAssetStatus.Pending || OutputPortStatus.Pending:
            return 'processing';
        case AbstractDataProductStatus.Active || TechnicalAssetStatus.Active || OutputPortStatus.Active:
            return 'success';
        case AbstractDataProductStatus.Archived || TechnicalAssetStatus.Archived || OutputPortStatus.Archived:
            return 'error';
        case AbstractDataProductStatus.Deleting:
            return 'error';
        default:
            return 'default';
    }
}

export function getDecisionStatusLabel(
    t: TFunction,
    status: DecisionStatus | InputPortRequestDecision,
    revokedAt?: string | null,
): string {
    if (status === DecisionStatus.Approved && revokedAt) {
        return t('Revoked');
    }
    switch (status) {
        case DecisionStatus.Pending:
            return t('Requested');
        case DecisionStatus.Approved:
            return t('Available');
        case DecisionStatus.Denied:
            return t('Rejected');
        case InputPortRequestDecision.Cancelled:
            return t('Cancelled');
        default:
            return t('Unknown');
    }
}

export function getDecisionStatusBadgeStatus(
    status: DecisionStatus | InputPortRequestDecision,
    revokedAt?: string | null,
): BadgeProps['status'] {
    if (status === DecisionStatus.Approved && revokedAt) {
        return 'error';
    }
    switch (status) {
        case DecisionStatus.Pending:
            return 'processing';
        case DecisionStatus.Approved:
            return 'success';
        case DecisionStatus.Denied:
            return 'error';
        case InputPortRequestDecision.Cancelled:
            return 'default';
        default:
            return 'default';
    }
}

export function getInputPortStatusLabel(t: TFunction, status: InputPortStatus): string {
    switch (status) {
        case InputPortStatus.Pending:
            return t('Requested');
        case InputPortStatus.Approved:
            return t('Available');
        case InputPortStatus.Denied:
            return t('Rejected');
        case InputPortStatus.Expired:
            return t('Expired');
        case InputPortStatus.Revoked:
            return t('Revoked');
        case InputPortStatus.Cancelled:
            return t('Cancelled');
        default:
            return t('Unknown');
    }
}

export function getInputPortStatusBadgeStatus(status: InputPortStatus): BadgeProps['status'] {
    switch (status) {
        case InputPortStatus.Pending:
            return 'default';
        case InputPortStatus.Approved:
            return 'success';
        case InputPortStatus.Denied:
            return 'error';
        case InputPortStatus.Expired:
            return 'error';
        case InputPortStatus.Revoked:
            return 'error';
        case InputPortStatus.Cancelled:
            return 'default';
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
