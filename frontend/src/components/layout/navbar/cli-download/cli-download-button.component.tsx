import { useGetVersionQuery } from '@/store/features/version/version-api-slice';
import { WindowsOutlined, AppleOutlined, LinuxOutlined, DownloadOutlined } from '@ant-design/icons';
import { Button, Dropdown } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './cli-download-button.module.scss';

export const DownloadCLIButton = () => {
    const { data: version } = useGetVersionQuery();
    const { t } = useTranslation();

    type DownloadLink = {
        label: string;
        suffix: string;
        icon: JSX.Element;
    };

    const windowsLinks: DownloadLink[] = [
        { label: 'X86/X64', suffix: 'Windows_x86_64.zip', icon: <WindowsOutlined /> },
        { label: 'ARM64', suffix: 'Windows_arm64.zip', icon: <WindowsOutlined /> },
        { label: 'i386', suffix: 'Windows_i386.zip', icon: <WindowsOutlined /> },
    ];
    const macLinks: DownloadLink[] = [
        { label: 'X86/X64', suffix: 'Darwin_x86_64.tar.gz', icon: <AppleOutlined /> },
        { label: 'ARM64', suffix: 'Darwin_arm64.tar.gz', icon: <AppleOutlined /> },
    ];
    const linuxLinks: DownloadLink[] = [
        { label: 'X86/X64', suffix: 'Linux_x86_64.tar.gz' },
        { label: 'ARM64', suffix: 'Linux_arm64.tar.gz' },
        { label: 'i386', suffix: 'Linux_i386.tar.gz' },
    ].map((link) => ({
        ...link,
        icon: <LinuxOutlined />,
    }));

    const downloadLink = (suffix: string, version: string) => {
        return `https://github.com/conveyordata/data-product-portal/releases/download/v${version}/data-product-portal_${suffix}`;
    };

    const item = (link: DownloadLink, version: string) => {
        return {
            label: (
                <a href={downloadLink(link.suffix, version)} target="_blank">
                    {link.label}
                </a>
            ),
            key: link.suffix,
            icon: link.icon,
        };
    };

    const isWindows = navigator.userAgent.includes('Win');
    const isMac = navigator.userAgent.includes('Mac');
    const isLinux = navigator.userAgent.includes('Linux');

    const menuLinks = isWindows
        ? windowsLinks
        : isMac
          ? macLinks
          : isLinux
            ? linuxLinks
            : windowsLinks.concat(macLinks).concat(linuxLinks);

    const menuProps = {
        items: menuLinks.map((link) => item(link, version?.version || 'latest')),
    };

    return (
        <Dropdown menu={menuProps} trigger={['click']} placement={'bottomRight'}>
            <Button shape={'circle'} className={styles.iconButton} icon={<DownloadOutlined />} />
        </Dropdown>
    );
};
