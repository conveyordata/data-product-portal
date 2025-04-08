---
title: Frontend
description: How to set up and run the frontend locally
sidebar_label: Frontend
sidebar_position: 4
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Typescript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Ant Design](https://img.shields.io/badge/-AntDesign-%230170FE?style=for-the-badge&logo=ant-design&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---

## Prerequisites

### Configuration (`config.local.js`)

All configuration values for this project are read from a `config.local.js` file in the frontend folder.

Check out [`config.docker.js`](https://github.com/conveyordata/data-product-portal/tree/main/frontend/config.docker.js) to see required/optional fields.

#### Minimal example:

```js title="config.local.js"
const config = {
  API_BASE_URL: 'http://localhost:5050',
  OIDC_ENABLED: true,
  OIDC_CLIENT_ID: '<YOUR_OIDC_CLIENT_ID>',
  OIDC_CLIENT_SECRET: '<YOUR_OIDC_CLIENT_SECRET>',
  OIDC_AUTHORITY: '<YOUR_OIDC_AUTHORITY>',
  OIDC_REDIRECT_URI: 'http://localhost:3000/',
  OIDC_POST_LOGOUT_REDIRECT_URI: 'http://localhost:3000/logout/',
};

module.exports = config;
```

### Docker (optional)

Install Docker from the [official site](https://docs.docker.com/get-docker/).

---

## Installation

Install dependencies:

```bash
npm install
```

---

## Local Execution

<Tabs>
<TabItem value="vite" label="Vite">

```bash
npm start
```

</TabItem>
<TabItem value="docker" label="Docker">

```bash
npm run copy-config
docker build . -t data-product-portal-frontend
docker run --name data-product-portal-frontend-container -p 3000:8080 data-product-portal-frontend
```

</TabItem>
</Tabs>

---

## Development Mode

Start development server with HMR:

```bash
npm run dev
```

---

## Linting and Formatting

### Commands

```bash
npm run lint       # Lint code
npm run lint:fix   # Auto-fix lint issues
npm run format     # Format code with Prettier
```

Make sure your IDE uses `.eslintrc.cjs` and `.prettierrc`.

---

## Translations

Using [i18next](https://www.i18next.com/).

### Usage with `useTranslation`

```tsx
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('key')}</h1>
      <p>{t('key2')}</p>
    </div>
  );
};
```

### Usage in hooks

```ts
import { useTranslation } from 'react-i18next';

const MyHook = () => {
  const { t } = useTranslation();

  return {
    message: t('key'),
  };
};
```

### Usage in utilities

```ts
import { i18n } from '@/i18n';

const myUtilityFunction = () => {
  return i18n.t('key');
};
```

### Extract Translations

```bash
npm run extract-translations
```

### Modify Translation Files

Edit `public/locales/{language}/translation.json`:

```json
{
  "key": "value",
  "key2": "value2"
}
```

---

## Interpolation

```tsx
<h1>{t('Welcome, {{name}}', { name: 'John' })}</h1>
```

```json
{
  "Welcome, {{name}}": "Welcome, {{name}}"
}
```

---

## Add New Languages

1. Create `public/locales/de/translation.json`
2. Update `i18n.ts`:

```ts title="i18n.ts"
export const languageEn = 'en';
export const languageDe = 'de';

const supportedLanguages = [languageEn, languageDe];
```

---

## Language Switching

```tsx
import { useTranslation } from 'react-i18next';
import i18n, { languageDe, languageEn } from '@/i18n';

const MyComponent = () => {
  const { t } = useTranslation();

  const switchLanguage = (lang) => i18n.changeLanguage(lang);

  return (
    <div>
      <button onClick={() => switchLanguage(languageEn)}>English</button>
      <button onClick={() => switchLanguage(languageDe)}>Deutsch</button>
    </div>
  );
};
```

---

## Debugging Translations

Enable debug mode in `i18n.ts`:

```ts
const isDevMode = import.meta.env.MODE === 'development';

i18n.init({
  debug: isDevMode,
  // ...
});
```

---

For more info, check [react-i18next documentation](https://react.i18next.com/getting-started)
