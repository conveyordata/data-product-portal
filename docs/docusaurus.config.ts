import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Data Product Portal',
  tagline: 'Open-source data product marketplace and process tool',
  favicon: 'img/favicon.svg',
  future: {
    'experimental_faster': true,
    v4: true,
  },

  // Set the production url of your site here
  url: 'https://data-product-portal.docs.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  // baseUrl: '/documentation',
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'conveyordata', // Usually your GitHub org/user name.
  projectName: 'data-product-portal', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  plugins: [
    [
      "posthog-docusaurus",
      {
        apiKey: "phc_NDxOG0gXQtkPItPFJXLOAQhLmbZw7v0SbIQesSWO4gc", // gitleaks:allow
        appUrl: "https://eu.i.posthog.com", // optional, defaults to "https://us.i.posthog.com"
        enableInDevelopment: false, // optional
      },
    ],
  ],
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    }
  },
  themes: ['@docusaurus/theme-mermaid'],
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/conveyordata/data-product-portal/tree/main/docs/',
            versions: {
							"0.3.x": {
								label: "0.3.x",
							path: "0.3.x"
							},
							"0.2.x": {
								label: "0.2.x",
							path: "0.2.x"
							},
              current: {
                label: "Latest (0.4.x)",
                path: "/",
                banner: 'none'
              },
            },
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
      [
        'redocusaurus',
        {
          specs: [
            {
              id: 'api',
              spec: 'static/openapi.json',
              route: '/docs/api/',
            },
          ],
          theme: {
            primaryColor: '#543EDC',
          },
        },
      ]
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Data Product Portal',
      logo: {
        alt: 'Data Product Portal Logo',
        src: 'img/favicon.svg',
      },
      items: [
        {to: '/docs/intro', label: 'Docs', position: 'left'},
        {to: '/docs/api', label: 'API spec', position: 'left'},
        {
          href: 'https://github.com/conveyordata/data-product-portal',
          label: 'GitHub',
          position: 'right',
        },
        {
          type: 'docsVersionDropdown',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/docs/getting-started/quickstart' },
            { label: 'User Guides', to: '/docs/category/user-guide' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'GitHub Issues', href: 'https://github.com/conveyordata/data-product-portal/issues' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Release notes', to: '/docs/release-notes' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Dataminded. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ["bash", "csharp", "java", "php", "ruby", "scala"],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
