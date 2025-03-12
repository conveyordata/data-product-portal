import { QuestionCircleOutlined } from '@ant-design/icons';
import { Row, Tooltip, type TooltipProps } from 'antd';
import type { PropsWithChildren, ReactNode } from 'react';

import styles from './question-tooltip.module.scss';

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
