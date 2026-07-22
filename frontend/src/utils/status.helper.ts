import type { BadgeProps } from 'antd';
import type { TFunction } from 'i18next';
import { AbstractDataProductStatus, TechnicalAssetStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { OutputPortStatus } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { DecisionStatus } from '@/types/roles';

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

export function getInputPortStatusLabel(t: TFunction, status: string): string {
    switch (status) {
        case 'pending':
            return t('Requested');
        case 'approved':
            return t('Available');
        case 'denied':
            return t('Rejected');
        case 'expired':
            return t('Expired');
        default:
            return t('Unknown');
    }
}

export function getInputPortStatusBadgeStatus(status: string): BadgeProps['status'] {
    switch (status) {
        case 'pending':
            return 'processing';
        case 'approved':
            return 'success';
        case 'denied':
            return 'error';
        case 'expired':
            return 'warning';
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
