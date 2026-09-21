import { ApiOutlined } from '@ant-design/icons';

// Dynamically import all SVG icons from the assets/icons directory
const icons = import.meta.glob('@/assets/icons/*.svg', {
    eager: true,
    query: '?react',
    import: 'default',
});

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
        return ApiOutlined as React.ComponentType<React.SVGProps<SVGSVGElement>>;
    }

    return icon as React.ComponentType<React.SVGProps<SVGSVGElement>>;
}
