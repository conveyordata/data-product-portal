import { WarningOutlined } from '@ant-design/icons';
import type { ComponentType, SVGProps } from 'react';

type IconComponent = ComponentType<SVGProps<SVGSVGElement>>;

// Helper function for eager loading
export function getIcon(name: string): IconComponent {
    const rawIcons = import.meta.glob('/src/assets/icons/*', {
        eager: true,
        import: 'default',
        query: '?react',
    });

    const icons: Record<string, IconComponent> = {};

    for (const fullPath in rawIcons) {
        // Extract the name from the path (e.g., "/src/assets/icons/aws-logo.svg" -> "aws-logo")
        const fileName = fullPath.split('/').pop() || '';
        const key = fileName.replace(/\.*$/, ''); // Remove .svg and any query string

        icons[key] = rawIcons[fullPath] as IconComponent;
    }

    const icon = icons[name];
    if (!icon) {
        console.warn(`Icon "${name}" not found. Available icons:`, Object.keys(icons));
        return WarningOutlined as IconComponent;
    }

    return icon;
}
