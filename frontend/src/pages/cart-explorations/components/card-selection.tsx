import Icon from '@ant-design/icons';
import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { Card, Flex } from 'antd';
import type * as React from 'react';
import styles from './card-selection.module.scss';

type CardSelectionOptions<T> = {
    title: string;
    description?: string;
    icon:
        | React.ComponentType<CustomIconComponentProps | React.SVGProps<SVGSVGElement>>
        | React.ForwardRefExoticComponent<CustomIconComponentProps>;
    value: T;
};

type Props<T> = {
    selectedChoice?: T;
    setSelectedChoice: (t: T) => void;
    options: CardSelectionOptions<T>[];
};

export const CardSelection = <T,>({ options, setSelectedChoice, selectedChoice }: Props<T>) => {
    return (
        <Flex gap={'middle'}>
            {options.map((option) => (
                <Card
                    key={option.value as string}
                    style={{ flex: 1 }}
                    hoverable
                    onClick={() => setSelectedChoice(option.value)}
                    className={selectedChoice === option.value ? styles.selectedCard : ''}
                >
                    <Card.Meta
                        avatar={
                            <Icon
                                component={option.icon}
                                className={
                                    selectedChoice === option.value
                                        ? styles.selectedCardIcon
                                        : styles.selectableCardIcon
                                }
                            />
                        }
                        title={option.title}
                        description={option.description}
                    />
                </Card>
            ))}
        </Flex>
    );
};
