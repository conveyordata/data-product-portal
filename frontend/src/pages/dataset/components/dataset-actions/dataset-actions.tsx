import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { CustomDropdownItemProps } from '@/types/shared';
import collibraLogo from '@/assets/icons/collibra-logo.svg?react';
import datahubLogo from '@/assets/icons/datahub-logo.svg?react';
import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';
import { TFunction } from 'i18next';
import styles from './dataset-actions.module.scss';
import { Flex } from 'antd';
import { DataPlataforms, DataPlatform } from '@/types/data-platform';

type Props = {
    datasetId: string;
    isCurrentDatasetOwner: boolean;
};

const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('Collibra'),
        value: DataPlataforms.Collibra,
        icon: collibraLogo,
    },
    { label: t('Datahub'), value: DataPlataforms.Datahub, icon: datahubLogo, disabled: true },
];

export function DatasetActions({ datasetId, isCurrentDatasetOwner }: Props) {
    const { t } = useTranslation();
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);

    async function handleAccessToData(environment: string, dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
        console.log(dataPlatform, environment, datasetId);
    }

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={isCurrentDatasetOwner}
                dataPlatforms={dataPlatforms}
                onDataPlatformClick={handleAccessToData}
                isDisabled
            />
        </Flex>
    );
}
