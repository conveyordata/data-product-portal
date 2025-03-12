import type { BadgeProps } from 'antd';
import type { TFunction } from 'i18next';

import { DataOutputStatus } from '@/types/data-output';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { DataProductStatus } from '@/types/data-product';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { DataProductMembershipStatus } from '@/types/data-product-membership';
import { Status } from '@/types/shared';

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

export function getDataProductDatasetLinkStatusLabel(t: TFunction, status: DataProductDatasetLinkStatus): string {
    switch (status) {
        case DataProductDatasetLinkStatus.Pending:
            return t('Requested');
        case DataProductDatasetLinkStatus.Approved:
            return t('Available');
        case DataProductDatasetLinkStatus.Denied:
            return t('Rejected');
        default:
            return t('Unknown');
    }
}

export function getDataOutputDatasetLinkStatusLabel(t: TFunction, status: DataOutputDatasetLinkStatus): string {
    switch (status) {
        case DataOutputDatasetLinkStatus.Pending:
            return t('Requested');
        case DataOutputDatasetLinkStatus.Approved:
            return t('Available');
        case DataOutputDatasetLinkStatus.Denied:
            return t('Rejected');
        default:
            return t('Unknown');
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

export function getDataProductMembershipStatusLabel(t: TFunction, role: DataProductMembershipStatus): string {
    switch (role) {
        case DataProductMembershipStatus.Approved:
            return t('Approved');
        case DataProductMembershipStatus.Denied:
            return t('Denied');
        default:
            return t('Pending');
    }
}
