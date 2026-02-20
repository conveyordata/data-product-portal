import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    ExclamationCircleOutlined,
    QuestionCircleOutlined,
} from '@ant-design/icons';
import type { TFunction } from 'i18next';
import type { DataQualityStatus } from '@/store/api/services/generated/dataProductsOutputPortsDataQualityApi';

export const getQualityStatusIcon = (status: DataQualityStatus) => {
    switch (status) {
        case 'success':
            return CheckCircleOutlined;
        case 'failure':
        case 'error':
            return CloseCircleOutlined;
        case 'warning':
            return ExclamationCircleOutlined;
        case 'unknown':
            return QuestionCircleOutlined;
        default:
            return QuestionCircleOutlined;
    }
};

export const getQualityStatusColor = (status: DataQualityStatus): string => {
    switch (status) {
        case 'success':
            return 'success';
        case 'failure':
        case 'error':
            return 'error';
        case 'warning':
            return 'warning';
        case 'unknown':
            return 'default';
        default:
            return 'default';
    }
};

export const formatQualityStatus = (status: DataQualityStatus, t: TFunction): string => {
    switch (status) {
        case 'success':
            return t('Passed');
        case 'failure':
            return t('Failed');
        case 'error':
            return t('Error');
        case 'warning':
            return t('Warning');
        case 'unknown':
            return t('Unknown');
        default:
            return t('Unknown');
    }
};
