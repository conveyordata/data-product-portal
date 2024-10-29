import s3BorderIcon from '@/assets/icons/s3-border-icon.svg?react';
import glueBorderIcon from '@/assets/icons/glue-border-icon.svg?react';
import databricksBorderIcon from '@/assets/icons/databricks-logo.svg?react';
import snowflakeBorderIcon from '@/assets/icons/snowflake-border-icon.svg?react';
import { TFunction } from 'i18next';

export function getDataOutputIcon(configuration_type: string|undefined) {
    switch (configuration_type) {
        case 'GlueDataOutput':
            return glueBorderIcon;
        case 'S3DataOutput':
            return s3BorderIcon;
        case 'DatabricksDataOutput':
            return databricksBorderIcon;
        case 'SnowflakeDataOutput':
            return snowflakeBorderIcon;
    }
}

export function getDataOutputType(configuration_type: string|undefined, t: TFunction) {
    switch (configuration_type) {
        case 'GlueDataOutput':
            return t('Glue');
        case 'SnowflakeDataOutput':
            return t('Snowflake');
        case 'S3DataOutput':
            return t('S3');
        case 'DatabricksDataOutput':
            return t('Databricks');
    }
}
