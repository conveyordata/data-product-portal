# CLI

## Linting

The CLI code is linted using [golangci-lint](https://golangci-lint.run/), you can find more info
on how to install it locally [here](https://golangci-lint.run/welcome/install/#local-installation).

After you have installed it you can lint the code with:

```bash
golangci-lint run --fix
```

This will fix all things that can be automatically fixed,
and will tell you were you need to make changes manually.
