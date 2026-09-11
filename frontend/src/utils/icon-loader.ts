import { createElement } from 'react';
import { AppConfig } from '@/config/app-config.ts';

// Dynamically import all SVG icons from the assets/icons directory
const icons = import.meta.glob('@/assets/icons/*.svg', {
    eager: true,
    query: '?react',
    import: 'default',
});

// A dynamically loaded plugin's icon (ADR-0024) isn't bundled at build time -
// it's fetched from the portal itself. `icon_name` for such a plugin is
// `dynamic:<plugin key>` (see PluginService._build_dynamic_plugin_metadata_response).
const DYNAMIC_PLUGIN_ICON_PREFIX = 'dynamic:';

function createDynamicPluginIcon(pluginKey: string): React.ComponentType<React.SVGProps<SVGSVGElement>> {
    return function DynamicPluginIcon({ className, style }: React.SVGProps<SVGSVGElement>) {
        return createElement('img', {
            // Same base URL every real API call resolves through
            // (src/store/common/axios-base-query.ts) - a bare relative path
            // only works when frontend and backend share an origin (the
            // Docker combined image), not in local dev with separate ports.
            src: `${AppConfig.getApiBaseURL()}/api/v2/plugins/dynamic/${pluginKey}/icon`,
            alt: '',
            className,
            style,
        });
    };
}

export function getIcon(iconName: string): React.ComponentType<React.SVGProps<SVGSVGElement>> {
    if (iconName.startsWith(DYNAMIC_PLUGIN_ICON_PREFIX)) {
        return createDynamicPluginIcon(iconName.slice(DYNAMIC_PLUGIN_ICON_PREFIX.length));
    }

    const iconPath = `/src/assets/icons/${iconName}`;
    const icon = icons[iconPath];

    if (!icon) {
        console.warn(`Icon not found: ${iconName}`);
        // Return a default icon or null
        return icons['/src/assets/icons/s3-logo.svg'] as React.ComponentType<React.SVGProps<SVGSVGElement>>;
    }

    return icon as React.ComponentType<React.SVGProps<SVGSVGElement>>;
}
