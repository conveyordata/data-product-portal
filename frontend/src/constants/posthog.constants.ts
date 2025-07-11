export enum PosthogEvents {
    PATHNAME_CHANGED = 'pathname_changed',
    PATHNAME_CHANGED_HOMEPAGE = 'pathname_changed_homepage',
    PATHNAME_CHANGED_DATA_PRODUCTS = 'pathname_changed_data_products',
    PATHNAME_CHANGED_MARKETPLACE = 'pathname_changed_marketplace',
    PATHNAME_CHANGED_EXPLORER = 'pathname_changed_explorer',
    PATHNAME_CHANGED_PEOPLE = 'pathname_changed_people',
    PATHNAME_CHANGED_AUDIT_LOGS = 'pathname_changed_audit_logs',
    PATHNAME_CHANGED_SETTINGS = 'pathname_changed_settings',

    HOMEPAGE_DATA_PRODUCTS_TAB_CLICKED = 'homepage_data_products_tab_clicked',
    HOMEPAGE_DATASETS_TAB_CLICKED = 'homepage_datasets_tab_clicked',

    REQUESTS_TAB_CLICKED = 'requests_tab_clicked',
    REQUESTS_ACCEPT = 'requests_accept',
    REQUESTS_REJECT = 'requests_reject',

    MARKETPLACE_SEARCHED_DATASET = 'marketplace_searched_dataset',
    MARKETPLACE_DATASET_TAB_CLICKED = 'marketplace_dataset_tab_clicked',
    MARKETPLACE_FILTER_USED = 'marketplace_filter_used',

    DATA_PRODUCTS_TAB_CLICKED = 'data_products_tab_clicked',
    DATA_PRODUCTS_FILTER_USED = 'data_products_filter_used',
    DATA_PRODUCTS_PLATFORM_ACCESS = 'data_products_platform_access',
    CREATE_DATA_PRODUCT_STARTED = 'create_data_product_started',
    CREATE_DATA_PRODUCT_COMPLETED = 'create_data_product_completed',
}
