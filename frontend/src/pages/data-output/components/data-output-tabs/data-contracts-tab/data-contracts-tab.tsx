import { Typography, Flex, Collapse } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-contracts-tab.module.scss';
import { useGetDataContractByOutputIdQuery } from '@/store/features/data-contracts/data-contracts-api-slice.ts';
import type { CollapseProps } from 'antd';

type Props = {
    dataOutputId: string;
};

export function DataContractsTab({ dataOutputId }: Props) {
    const { t } = useTranslation();

    const { data: dataContracts } = useGetDataContractByOutputIdQuery(dataOutputId);

    const items: CollapseProps['items'] = dataContracts?.map((dataContract) => ({
        key: dataContract.id,
        label: dataContract.table,
        children: <Flex vertical>
            <Typography.Paragraph>{ dataContract.description }</Typography.Paragraph>
            </Flex>
    }))

    return (
        <>
            <Flex vertical className={styles.container}>
                    <Collapse items={items}/>
            </Flex>
        </>
    );
}
