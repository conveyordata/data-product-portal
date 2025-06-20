import { useTranslation } from 'react-i18next';

function getSodaOrganization(): string {
    const org = process.env.SODA_ORGANIZATION;
    if (!org) {
        throw new Error('Environment variable SODA_ORGANIZATION is not set');
    }
    return org;
}

function getSodaFilterKey(): string {
    const { t } = useTranslation();
    const key = process.env.SODA_FILTER_KEY;
    if (!key) {
      return t('dataset');  // By default, we filter on dataset
    }
    return key;
}

// A dataset in Soda is basically a table or a view
export function getSodaDatasetUrl(filterValue: string): string {
    const returnUrl = `https://cloud.soda.io/datasets/overview?filters=('resourceAttributes.${getSodaFilterKey()}!'${filterValue}')_`;
    return `https://cloud.soda.io/sso/signin/${getSodaOrganization()}/?returnUrl=${encodeURIComponent(returnUrl)}`;
}
