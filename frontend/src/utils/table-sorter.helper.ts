export class Sorter<T> {
    stringSorter(accessor: (record: T) => string | undefined): (a: T, b: T) => number {
        return (a, b) => {
            const valA = accessor(a);
            const valB = accessor(b);

            if (valA === undefined && valB === undefined) return 0;
            if (valA === undefined) return 1;
            if (valB === undefined) return -1;

            return valA.localeCompare(valB);
        };
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
