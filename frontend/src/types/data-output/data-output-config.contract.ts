export type FieldDefinition = {
    name: string;
    type: 'string' | 'boolean' | 'select';
    required?: boolean;
    default?: string | boolean;
    label?: string;
    tooltip?: string;
    hidden?: boolean;
    depends_on?: string;
    consumer_aligned_locked?: boolean;
};

export type OutputConfig = {
    fields?: FieldDefinition[];
    technical_label?: string;
    subtitle_label?: string;
    platform?: string;
    type?: string;
    hasEnvironments?: boolean;
    hasConfig?: boolean;
    disabled?: boolean;
    marketplace?: boolean;
};
