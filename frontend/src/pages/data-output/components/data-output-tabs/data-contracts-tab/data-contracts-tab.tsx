import type { CollapseProps } from 'antd';
import { Collapse, Flex } from 'antd';

import { useGetDataContractByOutputIdQuery } from '@/store/features/data-contracts/data-contracts-api-slice.ts';

import { getCollapseItems } from './components/contract-collapse/collapse-item.component';
import styles from './data-contracts-tab.module.scss';

type Props = {
    dataOutputId: string;
};

export function DataContractsTab({ dataOutputId }: Props) {
    const { data: dataContracts } = useGetDataContractByOutputIdQuery(dataOutputId);

    if (!dataContracts) return null;

    const items: CollapseProps['items'] = getCollapseItems({ dataContracts });

    return (
        <>
            <Flex vertical className={styles.container}>
                <Collapse items={items} />
            </Flex>
        </>
    );
}
