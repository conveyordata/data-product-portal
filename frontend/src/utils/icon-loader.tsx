// Dynamically import all SVG icons from the assets/icons directory
const icons = import.meta.glob('@/assets/icons/*.svg', {
    eager: true,
    query: '?react',
    import: 'default',
});

// A plugin installed as a package ships its own icon, which the backend sends
// as a data URI because the frontend bundle cannot know about it. Wrapped in a
// component so callers treat both kinds of icon the same way.
export function getIconFromDataUri(dataUri: string): React.ComponentType<React.SVGProps<SVGSVGElement>> {
    return function PluginIcon(props: React.SVGProps<SVGSVGElement>) {
        return <img src={dataUri} alt="" width={props.width ?? 24} height={props.height ?? 24} />;
    };
}

export function getIcon(iconName: string): React.ComponentType<React.SVGProps<SVGSVGElement>> {
    const iconPath = `/src/assets/icons/${iconName}`;
    const icon = icons[iconPath];

    if (!icon) {
        console.warn(`Icon not found: ${iconName}`);
        // Return a default icon or null
        return icons['/src/assets/icons/s3-logo.svg'] as React.ComponentType<React.SVGProps<SVGSVGElement>>;
    }

    return icon as React.ComponentType<React.SVGProps<SVGSVGElement>>;
}
