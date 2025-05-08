import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx(styles.hero)}>
      <div className="container">
        <h1 className={styles.heroTitle}>
          {siteConfig.title}
        </h1>
        <p className={styles.heroSubtitle}>
          Scale your data product initiatives with self-service, governance by design, and a full view of your data landscape.
        </p>
        <div className={styles.buttons}>
          <Link
            className={styles.cta}
            to="/docs/user-guide/overview">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

function FeaturesSection() {
  const features = [
    {
      title: 'Self-Service by Design',
      description:
        'Empower teams to launch and manage data products independently, reducing dependency on central teams.',
    },
    {
      title: 'Governance Built In',
      description:
        'Ensure compliance and approval workflows are followed automatically with governance embedded in every step.',
    },
    {
      title: 'Platform-Agnostic',
      description:
        'Supports AWS, Azure, Databricks, and more. Integrates easily into your existing stack.',
    },
    {
      title: '360° Visibility',
      description:
        'Track the lifecycle of all data products, users, datasets, and outputs in one unified view.',
    },
    {
      title: 'Seamless Integrations',
      description:
        'Out-of-the-box integrations with Conveyor, Kubernetes, Helm, OIDC, and popular data platforms.',
    },
    {
      title: 'Built for Scale',
      description:
        'From a single team to an entire organization, scale your data operations without chaos.',
    },
  ];

  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Key Features</h2>
      <div className={styles.features}>
        {features.map((feature, idx) => (
          <div className={styles.featureCard} key={idx}>
            <h3 className={styles.featureTitle}>{feature.title}</h3>
            <p className={styles.featureDescription}>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function LinksSection() {
  return (
    <section className={clsx(styles.section, styles.sectionDark)}>
      <h2 className={styles.sectionTitle}>Resources</h2>
      <p className={styles.sectionText}>
        Learn more about how the Data Product Portal works, and how to extend or deploy it in your organization.
      </p>
      <div className={styles.linkGrid}>
        <Link className={styles.linkCard} to="/docs/intro">Documentation</Link>
        <Link className={styles.linkCard} to="https://github.com/conveyordata/data-product-portal">GitHub</Link>
        <Link className={styles.linkCard} to="https://conveyordata.com/portal-introducing-new-open-source-data-product-portal">Announcement Blog</Link>
        <Link className={styles.linkCard} to="/docs/getting-started/quickstart">Getting Started</Link>
      </div>
    </section>
  );
}

function GitHubStats() {
  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Open Source Insights</h2>
      <p className={styles.sectionText}>
        Built by the community, for the community. Join us in shaping the future of governed, scalable data product development.
      </p>
      <div className={styles.statsGrid}>
        <img src="https://img.shields.io/github/stars/conveyordata/data-product-portal?style=for-the-badge" alt="GitHub stars" />
        <img src="https://img.shields.io/github/forks/conveyordata/data-product-portal?style=for-the-badge" alt="GitHub forks" />
        <img src="https://img.shields.io/github/contributors/conveyordata/data-product-portal?style=for-the-badge" alt="GitHub contributors" />
        <img src="https://img.shields.io/github/issues/conveyordata/data-product-portal?style=for-the-badge" alt="GitHub issues" />
        <img src="https://img.shields.io/ossf-scorecard/github.com/conveyordata/data-product-portal.svg?style=for-the-badge" alt="OpenSSF Scorecard" />
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  return (
    <Layout
      title="Data Product Portal Docs"
      description="Documentation for the open source Data Product Portal">
      <HomepageHeader />
      <main>
        <FeaturesSection />
        <LinksSection />
        <GitHubStats />
      </main>
    </Layout>
  );
}
