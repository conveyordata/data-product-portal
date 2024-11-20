import { Typography, Flex, Collapse, List } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-contracts-tab.module.scss';
import { useGetDataContractByOutputIdQuery } from '@/store/features/data-contracts/data-contracts-api-slice.ts';
import type { CollapseProps } from 'antd';
import { SchemaTable } from './components/schema-table/schema-table.component';
import { CheckOutlined, CloseOutlined, ExclamationCircleOutlined, ExclamationOutlined, StopOutlined, WarningOutlined } from '@ant-design/icons';
import { getCollapseItems } from './components/contract-collapse/collapse-item.component';

type Props = {
    dataOutputId: string;
};

export function DataContractsTab({ dataOutputId }: Props) {
    const { t } = useTranslation();

    const { data: dataContracts } = useGetDataContractByOutputIdQuery(dataOutputId);

    if(!dataContracts) return null;

    const items: CollapseProps['items'] = getCollapseItems({dataContracts})

    return (
        <>
            <Flex vertical className={styles.container}>
                    <Collapse items={items}/>
            </Flex>
        </>
    );
}
