import type { TFunction } from 'i18next';

import databricksBorderIcon from '@/assets/icons/databricks-border-icon.svg?react';
import glueBorderIcon from '@/assets/icons/glue-border-icon.svg?react';
import redshiftBorderIcon from '@/assets/icons/redshift-border-icon.svg?react';
import s3BorderIcon from '@/assets/icons/s3-border-icon.svg?react';
import snowflakeBorderIcon from '@/assets/icons/snowflake-border-icon.svg?react';

export function getDataOutputIcon(configuration_type: string | undefined) {
    switch (configuration_type) {
        case 'GlueDataOutput':
            return glueBorderIcon;
        case 'S3DataOutput':
            return s3BorderIcon;
        case 'DatabricksDataOutput':
            return databricksBorderIcon;
        case 'SnowflakeDataOutput':
            return snowflakeBorderIcon;
        case 'RedshiftDataOutput':
            return redshiftBorderIcon;
    }
}

export function getDataOutputType(configuration_type: string | undefined, t: TFunction) {
    switch (configuration_type) {
        case 'GlueDataOutput':
            return t('Glue');
        case 'SnowflakeDataOutput':
            return t('Snowflake');
        case 'S3DataOutput':
            return t('S3');
        case 'DatabricksDataOutput':
            return t('Databricks');
        case 'RedshiftDataOutput':
            return t('Redshift');
    }
}
