import { DataProductStatus } from '@/types/data-product';
import { BadgeProps } from 'antd';
import i18n from '@/i18n.ts';
import { Status } from '@/types/shared';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { DataProductMembershipStatus } from '@/types/data-product-membership';

export function getStatusLabel(status: Status): string {
    switch (status) {
        case DataProductStatus.Pending:
            return i18n.t('Pending');
        case DataProductStatus.Active:
            return i18n.t('Active');
        case DataProductStatus.Archived:
            return i18n.t('Archived');
        default:
            return i18n.t('Unknown');
    }
}

export function getBadgeStatus(status: Status): BadgeProps['status'] {
    switch (status) {
        case DataProductStatus.Pending:
            return 'processing';
        case DataProductStatus.Active:
            return 'success';
        case DataProductStatus.Archived:
            return 'error';
        default:
            return 'default';
    }
}

export function getDataProductDatasetLinkStatusLabel(status: DataProductDatasetLinkStatus): string {
    switch (status) {
        case DataProductDatasetLinkStatus.Pending:
            return i18n.t('Requested');
        case DataProductDatasetLinkStatus.Approved:
            return i18n.t('Available');
        case DataProductDatasetLinkStatus.Denied:
            return i18n.t('Rejected');
        default:
            return i18n.t('Unknown');
    }
}

export function getDataProductDatasetLinkBadgeStatus(status: DataProductDatasetLinkStatus): BadgeProps['status'] {
    switch (status) {
        case DataProductDatasetLinkStatus.Pending:
            return 'processing';
        case DataProductDatasetLinkStatus.Approved:
            return 'success';
        case DataProductDatasetLinkStatus.Denied:
            return 'error';
        default:
            return 'default';
    }
}

export function getDataProductMembershipBadgeStatus(role: DataProductMembershipStatus): BadgeProps['status'] {
    switch (role) {
        case DataProductMembershipStatus.Approved:
            return 'success';
        case DataProductMembershipStatus.Denied:
            return 'default';
        default:
            return 'processing';
    }
}

export function getDataProductMembershipStatusLabel(role: DataProductMembershipStatus): string {
    switch (role) {
        case DataProductMembershipStatus.Approved:
            return i18n.t('Approved');
        case DataProductMembershipStatus.Denied:
            return i18n.t('Denied');
        default:
            return i18n.t('Pending');
    }
}
