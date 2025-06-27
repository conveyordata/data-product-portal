export type FieldDefinition = {
    name: string;
    type: 'string' | 'boolean' | 'select';
    required?: boolean;
    default?: string | boolean;
    label?: string;
    tooltip?: string;
    hidden?: boolean;
    depends_on?: string;
};

export type OutputConfig = {
    fields: FieldDefinition[];
    technical_label?: string;
    subtitle_label?: string;
};
