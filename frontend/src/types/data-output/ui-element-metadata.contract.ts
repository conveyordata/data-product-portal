type UIElementMetadata = {
    label: string;
    type: 'string' | 'select' | 'checkbox';
    required: boolean;
    name: string;
    tooltip?: string;
    options?: { values?: string[] };
    hidden?: boolean;
    pattern?: string;
    default?: any;
    initial_value?: any;
    value_prop_name?: string;
    depends_on?: { fieldName: string; value: any };
    select_mode?: 'tags' | 'multiple';
    max_count?: number;
    disabled?: boolean;
    use_namespace_when_not_source_aligned?: boolean;
    normalize_array?: boolean;
};
