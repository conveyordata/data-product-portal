import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import type { ComponentType, ForwardRefExoticComponent, SVGProps } from 'react';

export type SearchForm = {
    search: string;
};

export type CustomDropdownItemProps<T extends string = string> = {
    label: string;
    value: T;
    icon:
        | ComponentType<CustomIconComponentProps | SVGProps<SVGSVGElement>>
        | ForwardRefExoticComponent<CustomIconComponentProps>;
    disabled?: boolean;
    hasEnvironments?: boolean;
    hasConfig?: boolean;
    children?: CustomDropdownItemProps<string>[];
    form?: ComponentType;
};
