import styles from './question-tooltip.module.scss';
import type { PropsWithChildren, ReactNode } from 'react';
import { Row, Tooltip, type TooltipProps } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';

export default function QuestionTooltip(props: PropsWithChildren<TooltipProps>): ReactNode {
    const { children, ...tooltipProps } = props;

    return (
        <Row align={'middle'}>
            {children}
            <Tooltip {...tooltipProps}>
                <QuestionCircleOutlined className={styles.questionTooltip} />
            </Tooltip>
        </Row>
    );
}
