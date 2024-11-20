import { DataContractContract } from "@/types/data-contract";
import { CollapseProps, Flex, List, Space, Typography } from "antd";
import { SchemaTable } from "../schema-table/schema-table.component";
import styles from './collapse-item.module.scss';
import { CheckOutlined, CloseOutlined, StopOutlined, WarningOutlined } from '@ant-design/icons';

type Props = {
    dataContracts: DataContractContract[];
}

export const getCollapseItems = ({ dataContracts }: Props): CollapseProps['items'] => {
    return dataContracts.map((dataContract) => ({
        key: dataContract.id,
        label: dataContract.table,
        extra: genExtra(90),
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

        </Flex>),
    }))
}

interface ScoreLayOut {
    style: CSSModuleClasses[string],
    icon: JSX.Element
}

enum Score {
    BAD,
    AVERAGE,
    GOOD,
}

const scores: Record<Score, ScoreLayOut> = {
    [Score.BAD]: {
        style: styles.bad,
        icon: <CloseOutlined className={styles.bad}/>,
    },
    [Score.AVERAGE]: {
        style: styles.average,
        icon: <WarningOutlined className={styles.average}/>
    },
    [Score.GOOD]: {
        style: styles.good,
        icon: <CheckOutlined className={styles.good} />
    }
}

const returnLayout = (score: number): ScoreLayOut => {
    if (score >= 90) {
        return scores[Score.GOOD];
    } else if(score >= 50) {
        return scores[Score.AVERAGE];
    }else {
        return scores[Score.BAD];
    }
}

const genExtra = (score: number) => {
    const layout = returnLayout(score);
    return (<Typography.Text className={layout.style}> { layout.icon } {score}% </Typography.Text>)
}
