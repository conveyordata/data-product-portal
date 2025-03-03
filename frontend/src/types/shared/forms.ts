import { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { ComponentType, ForwardRefExoticComponent, SVGProps } from 'react';

import { DataPlatform } from '../data-platform';

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
