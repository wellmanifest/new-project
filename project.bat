@echo off
setlocal EnableDelayedExpansion

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

if "%1"=="" (
  call :usage
  exit /b 0
)

if /I "%1"=="help" call :usage & exit /b 0
if /I "%1"=="-h" call :usage & exit /b 0
if /I "%1"=="--help" call :usage & exit /b 0

set PIP_DISABLE_PIP_VERSION_CHECK=1

call :%1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%

:usage
echo Usage: project.bat ^<command^> [args]
echo.
echo Project commands:
echo   install             Install workspace dependencies from pnpm lockfile
echo   typecheck           Run TypeScript project references check
echo   lint                Run ESLint on source and tests
echo   format              Check formatting with Prettier
echo   test                Run TypeScript tests
echo   python-test         Run Python verifier tests
echo   example ^<name^>      Run one example scenario
echo   examples            Run all example scenarios
echo   example-chat ^<name^> Run one chat negotiation example
echo   examples-chat       Run all chat negotiation examples
echo   example-recruitment ^<name^> Run one recruitment example
echo   examples-recruitment Run all recruitment examples
echo   examples-index       Build one Markdown index for all example inputs, expected files and outputs
echo   makedocs            Generate README include menu and documentation indexes
echo   verify              Run typecheck, lint, format, tests, examples, Python tests and git diff check
echo   system-check        Run the full functional system test suite
echo   dev-backend         Start backend and static web demo
echo.
exit /b 0

:install
call corepack pnpm install --frozen-lockfile
exit /b %ERRORLEVEL%

:typecheck
call corepack pnpm run typecheck
exit /b %ERRORLEVEL%

:lint
call corepack pnpm run lint
exit /b %ERRORLEVEL%

:format
call corepack pnpm run format
exit /b %ERRORLEVEL%

:test
call corepack pnpm run test
exit /b %ERRORLEVEL%

:python-test
call corepack pnpm run python:test
exit /b %ERRORLEVEL%

:example
if "%2"=="" (
  echo Usage: project.bat example ^<name^>
  exit /b 2
)
call corepack pnpm run example:run -- %2
exit /b %ERRORLEVEL%

:examples
call corepack pnpm run examples:run
exit /b %ERRORLEVEL%

:example-chat
if "%2"=="" (
  echo Usage: project.bat example-chat ^<name^>
  exit /b 2
)
call corepack pnpm run example-chat:run -- %2
exit /b %ERRORLEVEL%

:examples-chat
call corepack pnpm run examples-chat:run
exit /b %ERRORLEVEL%

:example-recruitment
if "%2"=="" (
  echo Usage: project.bat example-recruitment ^<name^>
  exit /b 2
)
call corepack pnpm run example-recruitment:run -- %2
exit /b %ERRORLEVEL%

:examples-recruitment
call corepack pnpm run examples-recruitment:run
exit /b %ERRORLEVEL%

:examples-index
call corepack pnpm run examples:index -- %2
exit /b %ERRORLEVEL%

:makedocs
call corepack pnpm run docs:generate
exit /b %ERRORLEVEL%

:verify
call corepack pnpm run verify
exit /b %ERRORLEVEL%

:system-check
call corepack pnpm run system:check
exit /b %ERRORLEVEL%

:functional-test
call :system-check
exit /b %ERRORLEVEL%

:functional-tests
call :system-check
exit /b %ERRORLEVEL%

:dev-backend
call corepack pnpm run dev:backend
exit /b %ERRORLEVEL%
