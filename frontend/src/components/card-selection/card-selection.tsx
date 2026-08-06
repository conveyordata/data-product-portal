import { Card, Flex } from 'antd';
import type * as React from 'react';
import { cloneElement } from 'react';
import styles from './card-selection.module.scss';

type CardSelectionOption<T> = {
    title: string;
    description?: string;
    icon?: React.JSX.Element;
    value: T;
};

type Props<T> = {
    value?: T;
    onChange?: (t: T) => void;
    options: CardSelectionOption<T>[];
    style?: React.CSSProperties;
};

export const CardSelection = <T,>({ options, onChange, value, style }: Props<T>) => {
    return (
        <Flex gap="middle" style={style}>
            {options.map((option) => (
                <Card
                    key={option.value as string}
                    style={{ flex: 1 }}
                    hoverable
                    onClick={() => onChange?.(option.value)}
                    className={value === option.value ? styles.selectedCard : ''}
                >
                    <Card.Meta
                        avatar={
                            option.icon
                                ? cloneElement(option.icon, {
                                      className: [
                                          option.icon.props.className,
                                          value === option.value ? styles.selectedCardIcon : styles.selectableCardIcon,
                                      ]
                                          .filter(Boolean)
                                          .join(' '),
                                  })
                                : undefined
                        }
                        title={option.title}
                        description={option.description}
                    />
                </Card>
            ))}
        </Flex>
    );
};
