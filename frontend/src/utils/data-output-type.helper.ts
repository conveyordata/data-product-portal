import s3BorderIcon from '@/assets/icons/s3-border-icon.svg?react';
import glueBorderIcon from '@/assets/icons/glue-border-icon.svg?react';

export function getDataOutputIcon(configuration_type: string|undefined) {
    switch (configuration_type) {
        case 'GlueDataOutput':
            return glueBorderIcon;
        case 'S3DataOutput':
            return s3BorderIcon;
    }
}

export function getDataOutputType(configuration_type: string|undefined, t: TFunction) {
    switch (configuration_type) {
        case 'GlueDataOutput':
            return t('Glue');
        case 'S3DataOutput':
            return t('S3');
    }
}