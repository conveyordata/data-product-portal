import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    ExclamationCircleOutlined,
    QuestionCircleOutlined,
} from '@ant-design/icons';
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

export const formatQualityStatus = (status: DataQualityStatus): string => {
    switch (status) {
        case 'success':
            return 'Passed';
        case 'failure':
            return 'Failed';
        case 'error':
            return 'Error';
        case 'warning':
            return 'Warning';
        case 'unknown':
        default:
            return 'Unknown';
    }
};
