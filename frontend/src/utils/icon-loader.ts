// Dynamically import all SVG icons from the assets/icons directory
const icons = import.meta.glob('@/assets/icons/*.svg', {
    eager: true,
    query: '?react',
    import: 'default',
});

export function getIcon(iconName: string): any {
    const iconPath = `/src/assets/icons/${iconName}`;
    const icon = icons[iconPath];

    if (!icon) {
        console.warn(`Icon not found: ${iconName}`);
        // Return a default icon or null
        return icons['/src/assets/icons/s3-logo.svg'] || null;
    }

    return icon;
}
