import { ApiOutlined } from '@ant-design/icons';
import type { ComponentType, SVGProps } from 'react';

// Dynamically import all SVG icons from the assets/icons directory
const icons = import.meta.glob('@/assets/icons/*.svg', {
    eager: true,
    query: '?react',
    import: 'default',
});

// A plugin's icon is an <svg>, not an <img>: every caller sizes its icon with a
// `svg { width; height }` rule, and an <img> is left at its intrinsic size and
// clipped by the surrounding tile.
const pluginIcons = new Map<string, ComponentType<SVGProps<SVGSVGElement>>>();

export function getIconFromDataUri(dataUri: string): ComponentType<SVGProps<SVGSVGElement>> {
    const cached = pluginIcons.get(dataUri);
    if (cached) {
        return cached;
    }

    // biome-ignore lint/correctness/noComponentHookFactories: cached per data URI above, so the component identity is stable
    function PluginIcon(props: SVGProps<SVGSVGElement>) {
        return (
            <svg viewBox="0 0 100 100" aria-hidden="true" {...props}>
                <image href={dataUri} width="100" height="100" preserveAspectRatio="xMidYMid meet" />
            </svg>
        );
    }

    pluginIcons.set(dataUri, PluginIcon);
    return PluginIcon;
}

export function getIcon(iconName: string): ComponentType<SVGProps<SVGSVGElement>> {
    const iconPath = `/src/assets/icons/${iconName}`;
    const icon = icons[iconPath];

    if (!icon) {
        console.warn(`Icon not found: ${iconName}`);
        return ApiOutlined as ComponentType<SVGProps<SVGSVGElement>>;
    }

    return icon as ComponentType<SVGProps<SVGSVGElement>>;
}
