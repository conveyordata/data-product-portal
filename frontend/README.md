[![React][React]][React-url]
[![Typescript][Typescript]][Typescript-url]
[![Ant Design][Ant-Design]][Ant-Design-url]
[![Vite][Vite]][Vite-url]
[![Docker][Docker]][Docker-url]

# Front-end Getting Started

## Prerequisites

### Configuration (config.local.js file)
Both for local execution and local development, you need to specify some configuration arguments.
All configuration values for this project are read from a `config.local.js` file in the frontend folder.
Please look at [config.docker.js](config.docker.js) to see which values are mandatory and which can be omitted.
Then copy and paste the content of `config.docker.js` to `config.local.js` you created and replace values where necessary.

#### Minimal `config.local.js` file
```js
const config = {
  /**
   * The base URL of the API.
   * This is where your frontend will send API requests.
   */
  API_BASE_URL: 'http://localhost:5050',

  /**
   * Indicates whether OpenID Connect (OIDC) is enabled.
   * If true, OIDC is enabled.
   */
  OIDC_ENABLED: true,

  /**
   * The client ID for the OIDC provider.
   * This is used to identify the application to the OIDC provider.
   */
  OIDC_CLIENT_ID: '<YOUR_OIDC_CLIENT_ID>',

  /**
   * The client secret for the OIDC provider.
   * This is used along with the client ID to authenticate the application to the OIDC provider.
   */
  OIDC_CLIENT_SECRET: '<YOUR_OIDC_CLIENT_SECRET>',

  /**
   * The URL of the OIDC provider.
   * This is the endpoint where the application will communicate with the OIDC provider.
   */
  OIDC_AUTHORITY: '<YOUR_OIDC_AUTHORITY>',

  /**
   * The URL where the OIDC provider will redirect to after successful authentication.
   * This should be a route in the application that handles the authentication response.
   */
  OIDC_REDIRECT_URI: 'http://localhost:3000/',

  /**
   * The URL where the OIDC provider will redirect to after successful logout.
   * This should be a route in the application that handles post-logout actions.
   */
  OIDC_POST_LOGOUT_REDIRECT_URI: 'http://localhost:3000/logout/',
};

module.exports = config;
```

### Docker (only when you want to use Docker for local execution)
- Install [Docker](https://docs.docker.com/get-docker/) on your machine.

## Installation

In order to install all project dependencies using NPM, execute the command below.
  ```sh
  npm install
  ```

## Local Execution

In order to just run the frontend in a 'production-like' setup locally, you can choose between the 2 options below.

### Using Vite

- Copy configuration, build the project and start it in preview mode by simply executing the command below.
  ```sh
  npm start
  ```

### Using Docker

- Ensure your Docker service is running.
- Ensure a correct config.js file is available in the '/public' folder by executing the command below.
  ```sh
  npm run copy-config
  ```
- Build the Docker image by executing the command below.
  ```sh
  docker build . -t data-product-portal-frontend
  ```
- Run the Docker container by executing the command below.
  ```sh
  docker run --name data-product-portal-frontend-container -p 3000:8080  data-product-portal-frontend
  ```

## Local Development

### Run in dev mode
In order to run the project in development mode (auto refresh using HMR), execute the command below.
  ```sh
  npm run dev
  ```

### Linting and Formatting
This project has been set up using [eslint](https://eslint.org/) for linting and [prettier](https://prettier.io/) for formatting.
Respective configuration files are [.eslintrc.cjs](.eslintrc.cjs) and [.prettierrc](.prettierrc).
For ease of use we advise you to configure your IDE to use the above-mentioned files automatically on format or save actions.
If you want manual linting/formatting, you can always execute the commands below.

- For linting
  ```sh
  npm run lint
  ```
- For linting, including automatic fixes
  ```sh
  npm run lint:fix
  ```
- For formatting
  ```sh
  npm run format
  ```

### Translations
Static frontend translations are managed by using [i18next](https://www.i18next.com/).
Currently, the only language available is English, but this can be extended over time.
The English value of the translatable labels is deliberately being used as the translation key for ease of use.

#### Adding translatable fields

##### Using the useTranslation hook

- Use the `t` function from the useTranslation hook in your components.
  ```jsx
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

    export default MyComponent;
  ```

- Use the `t` function in your hooks.
  ```js
    import { useTranslation } from 'react-i18next';

    const MyHook = () => {
      const { t } = useTranslation();

      return {
        key: t('key'),
        key2: t('key2'),
      };
    };

    export default MyHook;
    ```

##### Using the i18n object

Use the `i18n` object directly inside utility functions.
  When using this method, make sure to import the `i18n` object
  from your i18n configuration file.
  To successfully consume your utility function, make sure that it is being consumed
  inside a functional component or hook.

```tsx
import { i18n } from '@/i18n';

const myUtilityFunction = () => {
  return i18n.t('key');
};

export default myUtilityFunction;
```

#### Extracting translatable fields

You can extract all translatable fields into JSON locales files that can be found in the 'public/locales/{language}'
folders (e.g. [en/translation.json](public/locales/en/translation.json)) by executing the command below.
  ```sh
  npm run extract-translations
  ```

#### Modifying translation labels

When you want to modify translation labels, you can simply look up the translatable key in the JSON locales files that
can be found in the 'public/locales/{language}' folders (e.g. [en/translation.json](public/locales/en/translation.json))
and change the label to the desired value.

All extracted keys will have an empty string as value by default. You can add the desired translation value to the key.

```json
{
  "key": "value",
  "key2": "value2"
}
```

Use the key in your code to display the translated value.

```tsx
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();

  return (
          <div>
            <h1>{t('key')}</h1> {/* Displays 'value' */}
            <p>{t('key2')}</p> {/* Displays 'value2' */}
          </div>
  );
};

export default MyComponent;
```

#### Interpolating variables in translations

You can interpolate variables in translations by using the `t` function from the useTranslation hook.

```jsx
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();

  return (
          <div>
            <h1>{t('Welcome, {{name}}', { name: 'John' })}</h1> {/* Displays 'Welcome, John' */}
          </div>
  );
};

export default MyComponent;
```

And in the JSON locales files, you can define the translation with the variable placeholder.

```json
{
  "Welcome, {{name}}": "Welcome, {{name}}"
}
```

#### Adding new languages

When you want to add a new language, you can create a new folder in the 'public/locales' folder with the language code
(e.g. 'de' for German) and add a translation file (e.g. 'public/locales/de/translation.json').
After that, you can add the new language to the 'i18n.ts' file list of supported languages.

```js
// ./src/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import I18NextHttpBackend from 'i18next-http-backend';

export const languageEn = 'en';
export const languageDe = 'de'; // <-- Added german language

const supportedLanguages = [languageEn, languageDe]; // <-- pass the new language code here

export const defaultLanguage = languageEn;

i18n
        // pass the i18n instance to react-i18next.
        .use(I18NextHttpBackend)
        .use(initReactI18next)
        // init i18next
        // for all options read: https://www.i18next.com/overview/configuration-options
        .init({
          lng: defaultLanguage,
          fallbackLng: defaultLanguage,
          supportedLngs: supportedLanguages,
          nsSeparator: false,
          keySeparator: false,
          missingKeyNoValueFallbackToKey: true,
          interpolation: {
            escapeValue: false, // not needed for react as it escapes by default
          },
          react: {
            useSuspense: true,
          },
          returnEmptyString: false,
        })
        .catch(() => null);

export default i18n;
```

#### Switching languages

You can easily implement a language switcher in the application by calling the i18n.changeLanguage function with the
desired language code.

```jsx
import { useTranslation } from 'react-i18next';
import i18n, { languageDe, languageEn } from '@/i18n';

const MyComponent = () => {
  const { t } = useTranslation();

  const switchLanguage = (language) => {
    i18n.changeLanguage(language);
  };

  return (
          <div>
            <button onClick={() => switchLanguage(languageEn)}>English</button>
            <button onClick={() => switchLanguage(languageDe)}>Deutsch</button>
            <h1>{t('key')}</h1>
          </div>
  );
};

export default MyComponent;
```

#### Debugging translations

When you want to debug translations, you can enable the debug mode in the i18n configuration file.
This will log all translation keys that are missing in the JSON locales files to the console, as well as the
relevant i18n events such as loaded translations, language changes, loaded namespaces, etc.

```js
// ./src/i18n.ts

// ...
const isDevMode = import.meta.env.MODE === 'development';

i18n
        // ...
        .init({
          // ...
          debug: isDevMode, // <-- Enable debug mode when in development mode
          //   ...
        })
// ...

export default i18n;
```

For more information on how to use i18next with React, please refer to
the [react-i18next documentation](https://react.i18next.com/getting-started).


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[React]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB

[React-url]: https://reactjs.org/

[Ant-Design]:https://img.shields.io/badge/-AntDesign-%230170FE?style=for-the-badge&logo=ant-design&logoColor=white

[Ant-Design-url]:https://ant.design

[Vite]:https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white

[Vite-url]:https://vitejs.dev/

[Typescript]:https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white

[Typescript-url]:https://www.typescriptlang.org

[Docker]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white

[Docker-url]: https://www.docker.com
