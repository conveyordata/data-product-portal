import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    ExclamationCircleOutlined,
    QuestionCircleOutlined,
} from '@ant-design/icons';
import type { TFunction } from 'i18next';
import type { DataQualityStatus } from '@/store/api/services/generated/outputPortDataQualityApi';

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
        default:
            return t('Unknown');
    }
};
