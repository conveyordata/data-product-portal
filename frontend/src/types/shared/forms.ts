import { ComponentType, ForwardRefExoticComponent, SVGProps } from 'react';
import { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';

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
    hasMenu?: boolean;
};
