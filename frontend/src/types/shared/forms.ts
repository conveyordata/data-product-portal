import { ComponentType, ForwardRefExoticComponent, SVGProps } from 'react';
import { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { DataPlatform } from '../data-platform';
import { DataOutputConfiguration } from '../data-output';

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
    hasConfig?: boolean;
    children?: CustomDropdownItemProps<DataPlatform>[];
    form?: ComponentType;
};
