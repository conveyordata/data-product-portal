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

export enum RenderLocation {
    DATA_OUTPUTS = 'data_outputs',
    MARKETPLACE = 'marketplace',
    DATA_PRODUCTS = 'data_products',
    ADD_OUTPUT = 'add_output',
}

export type OutputConfig = {
    fields?: FieldDefinition[];
    technical_label?: string;
    subtitle_label?: string;
    platform?: string;
    type?: string;
    has_environments?: boolean;
    marketplace?: boolean;
    icon: string;
    render_at: RenderLocation[];
};
