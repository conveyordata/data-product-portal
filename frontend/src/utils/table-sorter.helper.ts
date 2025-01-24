export class Sorter<T> {
    stringSorter(accessor: (record: T) => string): (a: T, b: T) => number {
        return (a, b) => accessor(a).localeCompare(accessor(b));
    }
    numberSorter(accessor: (record: T) => number): (a: T, b: T) => number {
        return (a, b) => accessor(a) - accessor(b);
    }
}
