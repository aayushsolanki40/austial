# Austial

**A NestJS-style, batteries-included web framework for Python, built on top of FastAPI.**

Austial gives Python the exact developer experience of [NestJS](https://nestjs.com/):
decorator-driven modules/controllers/providers, real constructor-based
dependency injection, the full request lifecycle (guards, pipes,
interceptors, exception filters, middleware), a config layer, a database
layer, Terminus-style health checks, a testing module -- and a CLI so you can
scaffold new projects and artifacts the same way `nest new`/`nest generate` do.

This repository is a **monorepo**: it contains both the reusable framework
(`austial/`, an installable package) and a sample app built with it (`src/`,
a working health-check API).

## Why

FastAPI is a fantastic ASGI toolkit, but it doesn't prescribe an application
architecture. Austial is opinionated on top of FastAPI the way Nest is
opinionated on top of Express/Fastify: modules own controllers and providers,
providers get dependency-injected by type, and the request pipeline
(guard → pipe → interceptor → handler → filter) is a first-class concept
instead of something you hand-roll with dependencies everywhere.

## Architecture at a glance

| NestJS | Austial |
|---|---|
| `@Module()` | `@Module(imports=, controllers=, providers=, exports=)` |
| `@Controller()` / `@Get()` etc. | `@Controller(prefix)` / `@Get/@Post/@Put/@Patch/@Delete/@Options/@Head` |
| `@Injectable()` | `@Injectable(scope=Scope.DEFAULT \| Scope.TRANSIENT)` |
| Constructor DI | Container resolves `__init__` type hints recursively, singleton by default |
| `NestFactory.create(AppModule)` | `AustialFactory.create(AppModule)` -> `AustialApplication` |
| `app.listen(3000)` | `await app.listen(8000)` |
| `CanActivate` / `@UseGuards` | `CanActivate` ABC + `ExecutionContext`, `@UseGuards(...)` |
| `NestInterceptor` / `@UseInterceptors` | `NestInterceptor` ABC (`intercept(context, call_next)`) + `@UseInterceptors(...)` |
| `PipeTransform` / `ValidationPipe` | `PipeTransform` ABC + `ValidationPipe` |
| `ExceptionFilter` / `@Catch` | `ExceptionFilter` ABC + `@Catch(...)`, default `AllExceptionsFilter` |
| `NestMiddleware`, `MiddlewareConsumer` | `NestMiddleware` ABC, `configure(consumer)` on modules |
| `ConfigModule.forRoot()` | `ConfigModule.for_root(env_file=".env")` / `ConfigService` |
| `TypeOrmModule.forRootAsync` | `DatabaseModule.for_root_async(use_factory=, inject=)` (SQLAlchemy async) |
| `@nestjs/terminus` | `austial.terminus.HealthCheckService` + `MemoryHealthIndicator`, `DatabaseHealthIndicator` |
| `@nestjs/testing` | `austial.testing.Test.create_testing_module(...).compile()` |
| `nest new` / `nest generate` | `austial new <name>` / `austial generate\|g module\|controller\|service\|resource <name>` |

### A note on file names

Nest names files with dots (`health.controller.ts`) because Node resolves
modules by explicit relative path strings. Python's `import a.b` instead
resolves `a` as a package and `b` as a submodule -- a literal file
`health.controller.py` isn't importable via a normal `import` statement. So
Austial uses underscore suffixes instead: `health_controller.py`,
`health_service.py`, `health_module.py`, `health_dto.py`. The directory
layout still mirrors Nest 1:1 -- one folder per feature under
`src/modules/`.

## Quickstart

```bash
uv sync                    # installs the framework + sample app deps
cp .env.example .env
uv run austial serve       # http://localhost:8000, auto-reload
```

Try it:

```bash
curl localhost:8000/                                          # {"message": "..."}
curl localhost:8000/health                                    # terminus-style health check
curl localhost:8000/health/protected                          # 403 Forbidden
curl -H "x-api-key: changeme" localhost:8000/health/protected  # 200 OK
curl localhost:8000/cats                                      # [] (generated via the CLI, see below)
open http://localhost:8000/docs                                # Swagger UI, free from FastAPI
```

Run the tests:

```bash
uv sync --all-extras
uv run pytest
```

## Linting, type-checking & pre-commit hooks

```bash
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy austial src tests # type-check

uv run pre-commit install --hook-type pre-commit --hook-type pre-push
uv run pre-commit run --all-files   # run every hook once, on demand
```

Once installed, `git commit` runs formatting/linting/type-checks automatically,
and `git push` also runs the test suite -- mirroring a typical Nest project's
husky + lint-staged setup. Projects scaffolded with `austial new` get the same
`.pre-commit-config.yaml` out of the box.

## Using the CLI

`austial new` scaffolds a brand-new project exactly like `nest new`:

```bash
uv run austial new my-app
cd my-app
uv sync
cp .env.example .env
uv run austial serve
```

> While Austial isn't published to PyPI yet, point new projects at this repo
> with `--link`: `austial new my-app --link /path/to/api.austial.com` -- this
> adds an editable `[tool.uv.sources]` entry so `uv sync` resolves `austial`
> from your local checkout.

`austial generate` (alias `austial g`) adds artifacts to an existing project,
patching `src/app_module.py`'s imports/`imports=[...]` array automatically --
just like `nest g`:

```bash
uv run austial generate module cats        # src/modules/cats/cats_module.py
uv run austial generate controller cats    # src/modules/cats/cats_controller.py
uv run austial generate service cats       # src/modules/cats/cats_service.py
uv run austial generate resource cats      # module + full CRUD controller/service/dto/entity
uv run austial g resource cats             # same as above, short alias
```

This repo's own `src/modules/cats/` was produced by running
`uv run austial generate resource cats` against this project -- it's not
hand-written, it's proof the generator works.

## Repository layout

```
api.austial.com/
├── pyproject.toml          # package "austial", console-script entry point
├── austial/                 # the framework (installable library)
│   ├── common/               # decorators, guards, interceptors, pipes, filters,
│   │                         # middleware, exceptions, logger
│   ├── core/                  # metadata/reflector, DI container, router builder,
│   │                         # AustialFactory / AustialApplication
│   ├── config/                 # ConfigModule / ConfigService
│   ├── database/                # DatabaseModule (SQLAlchemy async)
│   ├── terminus/                 # HealthCheckService + health indicators
│   ├── testing/                   # Test.create_testing_module(...)
│   └── cli/                        # `austial new` / `generate` / `serve` + templates
├── src/                      # sample app built with austial
│   ├── main.py                # entry point (mirrors Nest's main.ts)
│   ├── app_module.py            # root module
│   ├── app_controller.py / app_service.py
│   └── modules/
│       ├── health/                # GET /health, GET /health/protected
│       └── cats/                   # generated via `austial generate resource cats`
└── tests/
    ├── unit/health_service_spec.py
    └── e2e/app_e2e_spec.py
```

Test files use Nest's `*.spec.ts` naming convention (`*_spec.py` here);
`pyproject.toml`'s `[tool.pytest.ini_options]` is configured to discover them.

## Request lifecycle

Every route runs through the same pipeline Nest uses:

```
guards -> pipes -> interceptors (wrapping) -> handler -> exception filters
```

```python
from austial import Controller, Get, UseGuards, UseInterceptors
from austial.common.interceptors import TransformInterceptor

from .api_key_guard import ApiKeyGuard


@Controller("cats")
class CatsController:
    @Get(":id")
    @UseGuards(ApiKeyGuard)
    @UseInterceptors(TransformInterceptor())
    async def find_one(self, id: int):
        ...
```

Note path params use Nest's `:id` syntax (translated to FastAPI's `{id}`
under the hood), so route strings read exactly like their Nest counterparts.

## License

MIT
