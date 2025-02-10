import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { CustomDropdownItemProps } from '@/types/shared';
import collibraLogo from '@/assets/icons/collibra-logo.svg?react';
import datahubLogo from '@/assets/icons/datahub-logo.svg?react';
import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';
import { TFunction } from 'i18next';
import styles from './data-output-actions.module.scss';
import { Flex } from 'antd';
import { DataPlatforms, DataPlatform } from '@/types/data-platform';

type Props = {
    dataOutputId: string;
    isCurrentDataOutputOwner: boolean;
};

const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('Collibra'),
        value: DataPlatforms.Collibra,
        icon: collibraLogo,
    },
    { label: t('Datahub'), value: DataPlatforms.Datahub, icon: datahubLogo, disabled: true },
];

export function DataOutputActions({ dataOutputId, isCurrentDataOutputOwner }: Props) {
    const { t } = useTranslation();
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);

    async function handleAccessToData(environment: string, dataPlatform: string) {
        // Todo - implement endpoints to allow for dataset data access
        // All tiles are currently disabled
    }

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={isCurrentDataOutputOwner}
                dataPlatforms={dataPlatforms}
                onDataPlatformClick={handleAccessToData}
                isDisabled
            />
        </Flex>
    );
}
