import { Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';

import { ConsumersList } from './output-port-consumers-list.component';

type Props = {
    outputPortId: string;
    dataProductId: string;
    number_of_consumers?: number;
};

export function OutputPortCardTooltip({ outputPortId, dataProductId, number_of_consumers }: Props) {
    const { t } = useTranslation();

    return (
        <Tooltip
            placement="bottom"
            color="white"
            title={
                number_of_consumers && number_of_consumers > 0 ? (
                    <ConsumersList outputPortId={outputPortId} dataProductId={dataProductId} />
                ) : null
            }
        >
            {t('{{count}} consumers', { count: number_of_consumers })}
        </Tooltip>
    );
}
