import { Key } from 'react';

export class FilterSettings<T>{
    filterSearch: boolean;
    filters: FilterEntry[];
    onFilter: (value: boolean | Key, record: T) => boolean;

    constructor(data: T[], accessor: (record: T) => boolean | Key){
        this.filterSearch = true;
        this.filters = generateFilters<T>(data, accessor);
        this.onFilter = generateOnFilter(accessor);
    }
};

class FilterEntry{
    text: string;
    value: boolean | Key;

    constructor(text: string, value: boolean | Key) {
        this.text = text
        this.value = value
    }
};

function generateOnFilter<T>(accessor: (record: T) => boolean | Key): (value: boolean | Key, record: T) => boolean {
    return (value, record) => accessor(record) === value;
};

function generateFilters<T>(data: T[], accessor: (record: T) => boolean | Key) {
    const uniqueValues = Array.from(new Set(data.map(e => accessor(e)))).sort();
    return uniqueValues.map(value => new FilterEntry(String(value), value))
};
