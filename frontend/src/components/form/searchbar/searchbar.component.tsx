import { Flex, Form, FormInstance, FormItemProps, FormProps, Input, InputRef } from 'antd';
import { SearchProps } from 'antd/lib/input';
import { ForwardRefExoticComponent, ReactNode, RefAttributes } from 'react';

import { SearchForm } from '@/types/shared';

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
