import type { TFunction } from 'i18next';
import { type DataPlatform, DataPlatforms } from '@/types/data-platform';
import type { CustomDropdownItemProps } from '@/types/shared';
import { getIcon } from '@/utils/icon.helper';

export const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('AWS'),
        value: DataPlatforms.AWS,
        icon: getIcon('aws'),
        hasMenu: true,
        hasConfig: true,
        children: [
            {
                label: t('S3'),
                value: DataPlatforms.S3,
                icon: getIcon('s3'),
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
            {
                label: t('Glue'),
                value: DataPlatforms.Glue,
                icon: getIcon('glue'),
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
            {
                label: t('Redshift'),
                value: DataPlatforms.Redshift,
                icon: getIcon('redshift'),
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
        ],
    },
    {
        label: t('Conveyor'),
        value: DataPlatforms.Conveyor,
        icon: getIcon('conveyor'),
        hasMenu: false,
        hasConfig: false,
        children: [],
    },
    {
        label: t('Snowflake'),
        value: DataPlatforms.Snowflake,
        icon: getIcon('snowflake'),
        disabled: false,
        hasConfig: true,
        hasMenu: true,
        children: [],
    },
    {
        label: t('Databricks'),
        value: DataPlatforms.Databricks,
        icon: getIcon('databricks'),
        hasConfig: true,
        hasMenu: true,
        children: [],
    },
    {
        label: t('Tableau'),
        value: DataPlatforms.Tableau,
        icon: getIcon('tableau'),
        disabled: true,
        hasConfig: false,
        children: [],
    },
];
