import { Flex, Form, type FormInstance, type FormItemProps, type FormProps, Input, type InputRef } from 'antd';
import type { SearchProps } from 'antd/es/input';
import type { ForwardRefExoticComponent, ReactNode, RefAttributes } from 'react';

import type { SearchForm } from '@/types/shared';

import styles from './searchbar.module.scss';

type Props = {
    onSearch?: (values: SearchForm) => void;
    form: FormInstance<SearchForm>;
    searchProps?: ForwardRefExoticComponent<SearchProps & RefAttributes<InputRef>>;
    formProps?: FormProps<SearchForm>;
    formItemProps?: FormItemProps;
    placeholder?: string;
    actionButton?: ReactNode;
    isDisabled?: boolean;
};
export const Searchbar = ({
    searchProps,
    placeholder,
    onSearch,
    actionButton,
    isDisabled,
    formProps,
    formItemProps,
    form,
}: Props) => {
    const handleSearch = (values: SearchForm) => {
        onSearch?.(values);
    };

    return (
        <Flex className={styles.searchContainer}>
            <Form form={form} onFinish={handleSearch} disabled={isDisabled} {...formProps}>
                <Form.Item<SearchForm> name={'search'} {...formItemProps}>
                    <Input.Search placeholder={placeholder} allowClear {...searchProps} />
                </Form.Item>
            </Form>
            {actionButton}
        </Flex>
    );
};
