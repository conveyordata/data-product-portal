This folder is used to apply temporary patches to npm packages.

If you need to create a patch:
- make the needed modifications directly in your `node_modules` folder
- run `npx patch-package "name_of_the_package"`
- this will create the corresponding patch files in this directory

- We use the `postinstall` script in `package.json` to apply these patches automatically when `npm install` runs.
- Generated patches target a specific package version. When that package is updated, recreate its patch for the new
  version or remove the obsolete patch; stale patches can cause `patch-package` to fail during installation.
