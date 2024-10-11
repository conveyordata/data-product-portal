import { Key } from 'react';

export class FilterSettings<T>{
    filterSearch: boolean;
    filters: FilterEntry[];
    onFilter: (value: boolean | Key, record: T) => boolean;

    constructor(data: T[], accessor: (record: T) => any){
        this.filterSearch = true;
        this.filters = generateFilters<T>(data, accessor);
        this.onFilter = generateOnFilter(accessor);
    }
};

class FilterEntry{
    text: string;
    value: any;

    constructor(text: string, value: any) {
        this.text = text
        this.value = value
    }
};

function generateOnFilter<T>(accessor: (record: T) => any): (value: boolean | Key, record: T) => boolean {
    return (value, record) => accessor(record) === value;
};

function generateFilters<T>(data: T[], accessor: (record: T) => any) {
    const uniqueValues = Array.from(new Set(data.map(e => accessor(e))));
    return uniqueValues.map(value => new FilterEntry(String(value), value))
};
