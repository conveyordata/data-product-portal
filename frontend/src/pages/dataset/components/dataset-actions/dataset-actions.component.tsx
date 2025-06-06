import { Flex } from 'antd';
import type { TFunction } from 'i18next';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import collibraLogo from '@/assets/icons/collibra-logo.svg?react';
import datahubLogo from '@/assets/icons/datahub-logo.svg?react';
import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { type DataPlatform, DataPlatforms } from '@/types/data-platform';
import type { CustomDropdownItemProps } from '@/types/shared';

import styles from './dataset-actions.module.scss';

const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('Collibra'),
        value: DataPlatforms.Collibra,
        icon: collibraLogo,
    },
    { label: t('Datahub'), value: DataPlatforms.Datahub, icon: datahubLogo, disabled: true },
];

type Props = {
    datasetId: string;
};
export function DatasetActions({ datasetId }: Props) {
    const { t } = useTranslation();
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);

    async function handleAccessToData(environment: string, dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
        console.log(dataPlatform, environment, datasetId);
    }

    // const { data: request_access } = useCheckAccessQuery(
    //     {
    //         action: AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS,
    //     },
    // );
    const { data: read_integrations } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__READ_INTEGRATIONS,
        },
        {
            skip: !datasetId,
        },
    );

    // const canRequestAccess = request_access?.allowed ?? false;
    const canReadIntegrations = read_integrations?.allowed ?? false;

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={canReadIntegrations}
                dataPlatforms={dataPlatforms}
                onDataPlatformClick={handleAccessToData}
                isDisabled
            />
        </Flex>
    );
}
