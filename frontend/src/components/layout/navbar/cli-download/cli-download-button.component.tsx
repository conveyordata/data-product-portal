import { AppleOutlined, CodeOutlined, LinuxOutlined, WindowsOutlined } from '@ant-design/icons';
import { Button, Dropdown, Popover } from 'antd';
import { JSX } from 'react';
import { useTranslation } from 'react-i18next';

import { useGetVersionQuery } from '@/store/features/version/version-api-slice';

import styles from './cli-download-button.module.scss';

type DownloadItem = {
    label: string;
    suffix: string;
    icon: JSX.Element;
};

const createDownloadLink = (suffix: string, version: string) => {
    return `https://github.com/conveyordata/data-product-portal/releases/download/v${version}/data-product-portal_${suffix}`;
};

const downloadMenuItem = (item: DownloadItem, version: string) => {
    return {
        label: <a href={createDownloadLink(item.suffix, version)}>{item.label}</a>,
        key: item.suffix,
        icon: item.icon,
    };
};

const WINDOWS_DOWNLOAD_ITEMS: DownloadItem[] = [
    { label: 'X86/X64', suffix: 'Windows_x86_64.zip' },
    { label: 'ARM64', suffix: 'Windows_arm64.zip' },
    { label: 'i386', suffix: 'Windows_i386.zip' },
].map((item) => ({
    ...item,
    icon: <WindowsOutlined />,
}));

const MAC_DOWNLOAD_ITEMS: DownloadItem[] = [
    { label: 'X86/X64', suffix: 'Darwin_x86_64.tar.gz' },
    { label: 'ARM64', suffix: 'Darwin_arm64.tar.gz' },
].map((item) => ({
    ...item,
    icon: <AppleOutlined />,
}));

const LINUX_DOWNLOAD_ITEMS: DownloadItem[] = [
    { label: 'X86/X64', suffix: 'Linux_x86_64.tar.gz' },
    { label: 'ARM64', suffix: 'Linux_arm64.tar.gz' },
    { label: 'i386', suffix: 'Linux_i386.tar.gz' },
].map((item) => ({
    ...item,
    icon: <LinuxOutlined />,
}));

const isWindows = navigator.userAgent.includes('Win');
const isMac = navigator.userAgent.includes('Mac');
const isLinux = navigator.userAgent.includes('Linux');

const downloadItems = isWindows
    ? WINDOWS_DOWNLOAD_ITEMS
    : isMac
      ? MAC_DOWNLOAD_ITEMS
      : isLinux
        ? LINUX_DOWNLOAD_ITEMS
        : WINDOWS_DOWNLOAD_ITEMS.concat(MAC_DOWNLOAD_ITEMS).concat(LINUX_DOWNLOAD_ITEMS);

export const DownloadCLIButton = () => {
    const { t } = useTranslation();
    const { data: version } = useGetVersionQuery();

    const menuProps = {
        items: version ? downloadItems.map((item) => downloadMenuItem(item, version.version)) : [],
    };

    return (
        <Popover content={t('Download CLI executable')} trigger={'hover'} placement="left">
            <Dropdown menu={menuProps} trigger={['click']} placement={'bottom'} disabled={!version}>
                <Button shape={'circle'} className={styles.iconButton} icon={<CodeOutlined />} />
            </Dropdown>
        </Popover>
    );
};
