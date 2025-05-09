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
    useGetIntegrationUrlQuery
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';

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

    console.log('useGetIntegrationUrlQuery called with:', { 
        uuid: dataOutputId, 
        integration_type: DataPlatforms.Datahub 
    });

    const integrationUrl = useGetIntegrationUrlQuery({ 
        uuid: dataOutputId, 
        integration_type: DataPlatforms.Datahub 
    });

    async function handleTileClick(dataPlatform: DataPlatform) {
        switch (dataPlatform) {
            case DataPlatforms.Datahub:
                // log integrationUrl
                console.log(integrationUrl);
                console.log('Type of integrationUrl:', typeof integrationUrl);
                if (integrationUrl) {
                    if (integrationUrl.data && integrationUrl.data.url) {
                        console.log('Attributes of integrationUrl:', integrationUrl.data.url);
                        window.open(integrationUrl.data.url, '', 'noopener,noreferrer');
                    } else {
                        dispatchMessage({
                            type: 'error',
                            content: t(`Failed to get Datahub url for Data Output. DataOutputId: ${dataOutputId}, DataPlatform: ${dataPlatform}`),
                        });
                    }
                } else {
                    dispatchMessage({
                        type: 'error',
                        content: t(`Failed read Data Output Integration. DataOutputId: ${dataOutputId}, DataPlatform: ${dataPlatform}`),
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
