export type FieldDefinition = {
    name: string;
    type: 'string' | 'boolean' | 'select';
    required?: boolean;
    default?: string | boolean;
};

export type OutputConfig = {
    fields: FieldDefinition[];
    technical_label?: string;
    subtitle_label?: string;
};
