import { Flex } from 'antd';
import { TFunction } from 'i18next';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import collibraLogo from '@/assets/icons/collibra-logo.svg?react';
import datahubLogo from '@/assets/icons/datahub-logo.svg?react';
import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { CustomDropdownItemProps } from '@/types/shared';

import styles from './dataset-actions.module.scss';

type Props = {
    datasetId: string;
    isCurrentDatasetOwner: boolean;
};

const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('Collibra'),
        value: DataPlatforms.Collibra,
        icon: collibraLogo,
    },
    { label: t('Datahub'), value: DataPlatforms.Datahub, icon: datahubLogo, disabled: false },
];

export function DatasetActions({ datasetId, isCurrentDatasetOwner }: Props) {
    const { t } = useTranslation();
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);

    async function handleTileClick(dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
        console.log(dataPlatform, datasetId);
        switch (dataPlatform) {
            case DataPlatforms.Datahub:
                const datahubUrl = "https://datahub.neo-platform-services.dna.luminus.be/";
                window.open(datahubUrl, '_blank');
                break;
            default:
                break;
        }
    }

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={isCurrentDatasetOwner}
                dataPlatforms={dataPlatforms}
                onTileClick={handleTileClick}
            />
        </Flex>
    );
}
