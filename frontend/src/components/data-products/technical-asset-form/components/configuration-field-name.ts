export function configurationFieldName<T extends string>(name: T): ['configuration', T] {
    return ['configuration', name];
}
