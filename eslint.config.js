import tseslint from "typescript-eslint";

export default tseslint.config({
  ignores: ["dist/**", "node_modules/**", "verifier/.venv/**"],
  rules: {
    "no-eval": "error",
    "no-new-func": "error"
  }
});
