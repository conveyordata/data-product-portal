import { Typography, Flex, Collapse, List } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-contracts-tab.module.scss';
import { useGetDataContractByOutputIdQuery } from '@/store/features/data-contracts/data-contracts-api-slice.ts';
import type { CollapseProps } from 'antd';
import { SchemaTable } from './components/schema-table/schema-table.component';

type Props = {
    dataOutputId: string;
};

export function DataContractsTab({ dataOutputId }: Props) {
    const { t } = useTranslation();

    const { data: dataContracts } = useGetDataContractByOutputIdQuery(dataOutputId);

    if(!dataContracts) return null;

    const items: CollapseProps['items'] = dataContracts?.map((dataContract) => ({
        key: dataContract.id,
        label: dataContract.table,
        children: (
        <Flex vertical>
            <Typography.Title level={5}>Description</Typography.Title>
            <Typography.Paragraph italic>{ dataContract.description }</Typography.Paragraph>

            {
                dataContract.service_level_objectives.length > 0 &&
                (
                    <>
                        <Typography.Title level={5}>Service Level Objectives</Typography.Title>
                        <List
                            split={false}
                            dataSource={dataContract.service_level_objectives}
                            renderItem={(objective) => (
                                <List.Item>
                                    [{objective.severity}] {objective.type}: {objective.value}
                                </List.Item>
                            )}
                        />
                    </>
                )
            }

            <Typography.Title level={5}>Schema</Typography.Title>
            {
                dataContract.checks.length > 0 &&
                (<Typography.Text>Checks: { dataContract.checks.join(', ') }</Typography.Text>)
            }
            <SchemaTable dataContractId={ dataContract.id } />

        </Flex>)
    }))

    return (
        <>
            <Flex vertical className={styles.container}>
                    <Collapse items={items}/>
            </Flex>
        </>
    );
}
