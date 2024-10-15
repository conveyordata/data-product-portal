import { DataProductStatus } from '@/types/data-product';
import { DataOutputStatus } from '@/types/data-output';
import { BadgeProps } from 'antd';
import i18n from '@/i18n.ts';
import { Status } from '@/types/shared';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { DataProductMembershipStatus } from '@/types/data-product-membership';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';

export function getStatusLabel(status: Status): string {
    switch (status) {
        case DataProductStatus.Pending || DataOutputStatus.Pending:
            return i18n.t('Pending');
        case DataProductStatus.Active || DataOutputStatus.Active:
            return i18n.t('Active');
        case DataProductStatus.Archived || DataOutputStatus.Archived:
            return i18n.t('Archived');
        default:
            return i18n.t('Unknown');
    }
}

export function getBadgeStatus(status: Status): BadgeProps['status'] {
    switch (status) {
        case DataProductStatus.Pending || DataOutputStatus.Pending:
            return 'processing';
        case DataProductStatus.Active || DataOutputStatus.Active:
            return 'success';
        case DataProductStatus.Archived || DataOutputStatus.Archived:
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

export function getDataOutputDatasetLinkStatusLabel(status: DataOutputDatasetLinkStatus): string {
    switch (status) {
        case DataOutputDatasetLinkStatus.Pending:
            return i18n.t('Requested');
        case DataOutputDatasetLinkStatus.Approved:
            return i18n.t('Available');
        case DataOutputDatasetLinkStatus.Denied:
            return i18n.t('Rejected');
        default:
            return i18n.t('Unknown');
    }
}

export function getDataOutputDatasetLinkBadgeStatus(status: DataOutputDatasetLinkStatus): BadgeProps['status'] {
    switch (status) {
        case DataOutputDatasetLinkStatus.Pending:
            return 'processing';
        case DataOutputDatasetLinkStatus.Approved:
            return 'success';
        case DataOutputDatasetLinkStatus.Denied:
            return 'error';
        default:
            return 'default';
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
