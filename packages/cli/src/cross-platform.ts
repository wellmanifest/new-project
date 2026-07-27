import { pathToFileURL } from "node:url";
import os from "node:os";
import path from "node:path";

/**
 * Cross-platform path helpers for the Office DSL CLI.
 *
 * Commands accept both Windows (`\`) and POSIX (`/`) separators, as well as
 * relative, absolute, and `file://` paths. These helpers normalize inputs to
 * platform-correct file paths and import URLs.
 */
export function normalizePathArgument(input: string): string {
  if (!input) return "";
  // Accept file:// URLs.
  if (input.startsWith("file://")) return fileUrlToPath(input);
  // Normalize separators to the current platform.
  return path.resolve(input.replace(/\//g, path.sep).replace(/\\/g, path.sep));
}

/**
 * Convert a file:// URL to a platform path. Falls back to URL decode on
 * Windows where pathFromFileURL exists, otherwise uses simple stripping.
 */
export function fileUrlToPath(url: string): string {
  const decoded = decodeURIComponent(url.replace(/^file:\/\//, ""));
  if (process.platform === "win32") {
    // Windows file URLs may start with a host or a leading slash before the
    // drive letter (file:///C:/... or file://server/share/...).
    const withoutHost = decoded.replace(/^\/([a-zA-Z]:\/)/, "$1");
    return path.resolve(withoutHost.replace(/\//g, "\\"));
  }
  return path.resolve(decoded);
}

/**
 * Build a `file://` URL suitable for dynamic `import()` on any platform,
 * including Windows paths with drive letters and backslashes.
 */
export function pathToImportUrl(filePath: string): string {
  return pathToFileURL(path.resolve(filePath)).href;
}

/**
 * Current platform name used for test assertions and output messages.
 */
export function platformName(): "win32" | "linux" | "darwin" | "other" {
  const platform = os.platform();
  if (platform === "win32") return "win32";
  if (platform === "linux") return "linux";
  if (platform === "darwin") return "darwin";
  return "other";
}

/**
 * True when the CLI is running on a Windows host.
 */
export function isWindows(): boolean {
  return process.platform === "win32";
}

/**
 * Convert a path to the style used by the other major platform. Useful for
 * exercising cross-platform normalization in tests.
 */
export function toAlternateSeparator(filePath: string): string {
  return isWindows() ? filePath.replace(/\\/g, "/") : filePath.replace(/\//g, "\\");
}
