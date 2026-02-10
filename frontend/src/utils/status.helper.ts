import type { BadgeProps } from 'antd';
import type { TFunction } from 'i18next';
import { DataProductStatus, TechnicalAssetStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { OutputPortStatus } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { DecisionStatus } from '@/types/roles';

export function getStatusLabel(
    t: TFunction,
    status: TechnicalAssetStatus | DataProductStatus | OutputPortStatus,
): string {
    switch (status) {
        case DataProductStatus.Pending || TechnicalAssetStatus.Pending || OutputPortStatus.Pending:
            return t('Pending');
        case DataProductStatus.Active || TechnicalAssetStatus.Active || OutputPortStatus.Active:
            return t('Active');
        case DataProductStatus.Archived || TechnicalAssetStatus.Archived || OutputPortStatus.Archived:
            return t('Deleted');
        default:
            return t('Unknown');
    }
}

export function getBadgeStatus(
    status: TechnicalAssetStatus | DataProductStatus | OutputPortStatus,
): BadgeProps['status'] {
    switch (status) {
        case DataProductStatus.Pending || TechnicalAssetStatus.Pending || OutputPortStatus.Pending:
            return 'processing';
        case DataProductStatus.Active || TechnicalAssetStatus.Active || OutputPortStatus.Active:
            return 'success';
        case DataProductStatus.Archived || TechnicalAssetStatus.Archived || OutputPortStatus.Archived:
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
