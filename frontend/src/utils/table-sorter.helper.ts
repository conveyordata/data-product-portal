export class Sorter<T> {
    stringSorter(accessor: (record: T) => string): (a: T, b: T) => number {
        return (a, b) => accessor(a).localeCompare(accessor(b));
    }

    numberSorter(accessor: (record: T) => number): (a: T, b: T) => number {
        return (a, b) => accessor(a) - accessor(b);
    }

    cascadedSorter(...sorters: ((a: T, b: T) => number)[]): (a: T, b: T) => number {
        return (a, b) => {
            for (const sorter of sorters) {
                const result = sorter(a, b);
                if (result !== 0) {
                    return result;
                }
            }
            return 0;
        };
    }
}
