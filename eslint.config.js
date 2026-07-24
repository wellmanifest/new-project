import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      "verifier/.venv/**",
      "verifier/.pytest_cache/**",
      "verifier/pytest-cache-files-*/**"
    ]
  },
  ...tseslint.configs.recommended,
  {
    files: ["**/*.ts", "**/*.js"],
    rules: {
      "no-eval": "error",
      "no-new-func": "error"
    }
  }
);
