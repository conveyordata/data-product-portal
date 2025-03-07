import { Flex } from 'antd';
import type { TFunction } from 'i18next';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import collibraLogo from '@/assets/icons/collibra-logo.svg?react';
import datahubLogo from '@/assets/icons/datahub-logo.svg?react';
import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { DataPlatform, DataPlatforms } from '@/types/data-platform';
import { CustomDropdownItemProps } from '@/types/shared';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

import {
    useGetIntegrationUrlMutation
} from '@/store/features/data-products/data-products-api-slice.ts';

import styles from './data-output-actions.module.scss';

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
    { label: t('Datahub'), value: DataPlatforms.Datahub, icon: datahubLogo, disabled: false },
];

export function DataOutputActions({ dataOutputId, isCurrentDataOutputOwner }: Props) {
    const { t } = useTranslation();
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const getIntegrationUrl = useGetIntegrationUrlMutation();

    async function handleTileClick(dataPlatform: DataPlatform) {
        switch (dataPlatform) {
            case DataPlatforms.Datahub:
                try {
                    const url = await getIntegrationUrl({ id: dataOutputId, dataPlatform }).unwrap();
                    if (url) {
                        window.open(url, '_blank');
                    } else {
                        dispatchMessage({
                            type: 'error',
                            content: t('Failed to get Datahub url'),
                        });
                    }
                } catch (_error) {
                    dispatchMessage({
                        type: 'error',
                        content: t('Failed to get Datahub url'),
                    });
                }
                break;
            default:
                break;
        }
    }

    return (
        <Flex vertical className={styles.actionsContainer}>
            <DataAccessTileGrid
                canAccessData={isCurrentDataOutputOwner}
                dataPlatforms={dataPlatforms}
                onTileClick={handleTileClick}
            />
        </Flex>
    );
}
