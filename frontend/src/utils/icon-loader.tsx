import { ApiOutlined } from '@ant-design/icons';

// Dynamically import all SVG icons from the assets/icons directory
const icons = import.meta.glob('@/assets/icons/*.svg', {
    eager: true,
    query: '?react',
    import: 'default',
});

// A plugin's icon is an <svg>, not an <img>: every caller sizes its icon with a
// `svg { width; height }` rule, and an <img> is left at its intrinsic size and
// clipped by the tile around it.
const pluginIcons = new Map<string, React.ComponentType<React.SVGProps<SVGSVGElement>>>();

export function getIconFromDataUri(dataUri: string): React.ComponentType<React.SVGProps<SVGSVGElement>> {
    const cached = pluginIcons.get(dataUri);
    if (cached) {
        return cached;
    }

    function PluginIcon(props: React.SVGProps<SVGSVGElement>) {
        return (
            <svg viewBox="0 0 100 100" aria-hidden="true" {...props}>
                <image href={dataUri} width="100" height="100" preserveAspectRatio="xMidYMid meet" />
            </svg>
        );
    }

    pluginIcons.set(dataUri, PluginIcon);
    return PluginIcon;
}

export function getIcon(iconName: string): React.ComponentType<React.SVGProps<SVGSVGElement>> {
    const iconPath = `/src/assets/icons/${iconName}`;
    const icon = icons[iconPath];

    if (!icon) {
        console.warn(`Icon not found: ${iconName}`);
        return ApiOutlined as React.ComponentType<React.SVGProps<SVGSVGElement>>;
    }

    return icon as React.ComponentType<React.SVGProps<SVGSVGElement>>;
}
