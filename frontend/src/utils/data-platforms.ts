import type { TFunction } from 'i18next';

import awsLogo from '@/assets/icons/aws-logo.svg?react';
import redshiftLogo from '@/assets/icons/aws-redshift-logo.svg?react';
import conveyorLogo from '@/assets/icons/conveyor-logo.svg?react';
import databricksLogo from '@/assets/icons/databricks-logo.svg?react';
import glueLogo from '@/assets/icons/glue-logo.svg?react';
import s3Logo from '@/assets/icons/s3-logo.svg?react';
import snowflakeLogo from '@/assets/icons/snowflake-logo.svg?react';
import tableauLogo from '@/assets/icons/tableau-logo.svg?react';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { CustomDropdownItemProps } from '@/types/shared';

export const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('AWS'),
        value: DataPlatforms.AWS,
        icon: awsLogo,
        hasMenu: true,
        hasConfig: true,
        children: [
            {
                label: t('S3'),
                value: DataPlatforms.S3,
                icon: s3Logo,
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
            {
                label: t('Glue'),
                value: DataPlatforms.Glue,
                icon: glueLogo,
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
            {
                label: t('Redshift'),
                value: DataPlatforms.Redshift,
                icon: redshiftLogo,
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
        ],
    },
    {
        label: t('Conveyor'),
        value: DataPlatforms.Conveyor,
        icon: conveyorLogo,
        hasMenu: false,
        hasConfig: false,
        children: [],
    },
    {
        label: t('Snowflake'),
        value: DataPlatforms.Snowflake,
        icon: snowflakeLogo,
        disabled: false,
        hasConfig: true,
        hasMenu: true,
        children: [],
    },
    {
        label: t('Databricks'),
        value: DataPlatforms.Databricks,
        icon: databricksLogo,
        hasConfig: true,
        hasMenu: true,
        children: [],
    },
    {
        label: t('Tableau'),
        value: DataPlatforms.Tableau,
        icon: tableauLogo,
        disabled: true,
        hasConfig: false,
        children: [],
    },
];
