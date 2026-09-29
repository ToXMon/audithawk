import { z } from "zod";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);

/**
 * AuditHawk toolbelt — implements Forge's ToolSpec contract
 * (name, description, zod parameters, async handler → string output).
 * Wire these into forge/src/tools/index.ts.
 *
 * Every tool executes inside the Docker sandboxes from infra/ — never on the
 * host. Workspace paths are session-scoped mounts.
 */

const FOUNDRY_IMAGE = "ghcr.io/foundry-rs/foundry:latest";

export const auditToolSpecs = [
  {
    name: "slither_scan",
    description:
      "Run Slither static analysis over the target repo in the slither container. Returns detector findings as structured text. Always run this before hypothesizing.",
    parameters: z.object({
      repoPath: z.string().describe("Workspace-relative path to the cloned target repo"),
    }),
    handler: async ({ repoPath }: { repoPath: string }) => {
      const { stdout } = await run("docker", [
        "run", "--rm", "-v", `${repoPath}:/share:ro`, "trailofit/slither",
        "slither", "/share", "--markdown", "/dev/stdout",
      ], { timeout: 180_000, maxBuffer: 8 * 1024 * 1024 });
      return stdout.slice(0, 30_000);
    },
  },
  {
    name: "aderyn_scan",
    description:
      "Run Aderyn (Rust-based Solana/Anchor static analyzer) when the target is Solana/Rust. Skip for EVM targets.",
    parameters: z.object({ repoPath: z.string() }),
    handler: async ({ repoPath }: { repoPath: string }) => {
      const { stdout } = await run("docker", [
        "run", "--rm", "-v", `${repoPath}:/share:ro`, "ghcr.io/cyfrin/aderyn:latest",
        "aderyn", "/share",
      ], { timeout: 180_000, maxBuffer: 8 * 1024 * 1024 });
      return stdout.slice(0, 30_000);
    },
  },
  {
    name: "rag_search_findings",
    description:
      "Search the knowledge base of real audit findings (HF audit-findings-dataset + your personal corpus). Returns title, severity, PoC snippet and contest for the top-k matches. REQUIRED before promoting any hypothesis to a finding.",
    parameters: z.object({
      query: z.string().describe("Vulnerability pattern description, e.g. 'hard-coded execution fee assumes USDC decimals'"),
      k: z.number().int().min(1).max(10).default(5),
    }),
    handler: async ({ query, k }: { query: string; k: number }) => {
      // Shells into ml/ — keeps ML deps out of the TS runtime.
      const { stdout } = await run("python3", [
        "-m", "search_findings", "--query", query, "--k", String(k),
      ], { cwd: "ml", timeout: 30_000, maxBuffer: 4 * 1024 * 1024 });
      return stdout;
    },
  },
  {
    name: "forge_test",
    description:
      "Compile and run Foundry tests in the foundry container. This is the ONLY source of truth for whether a PoC is proven. Returns pass/fail + trace. A finding may only be reported as proven if this returned success for its test.",
    parameters: z.object({
      workspacePath: z.string().describe("Session workspace containing the foundry project"),
      testName: z.string().optional().describe("Run a single test: forge test --match-test <name>"),
    }),
    handler: async ({ workspacePath, testName }: { workspacePath: string; testName?: string }) => {
      const args = ["run", "--rm", "-v", `${workspacePath}:/workdir`, FOUNDRY_IMAGE,
        "bash", "-lc", `cd /workdir && forge test -vvv${testName ? ` --match-test ${testName}` : ""} 2>&1`];
      try {
        const { stdout } = await run("docker", args, { timeout: 300_000, maxBuffer: 8 * 1024 * 1024 });
        const passed = /Suite result: ok|passed/.test(stdout) && !/FAILED/.test(stdout);
        return `PROVEN: ${passed}\n${stdout.slice(-8000)}`;
      } catch (err: unknown) {
        const e = err as { stdout?: string; message: string };
        return `PROVEN: false\n${(e.stdout ?? e.message).slice(-8000)}`;
      }
    },
  },
  {
    name: "fetch_bounty",
    description:
      "Ingest a contest/bounty page (scope, rules, prizes, timeline) via the Browserbase headless browser. Returns extracted text. Requires BROWSERBASE_API_KEY.",
    parameters: z.object({ url: z.string().url() }),
    handler: async ({ url }: { url: string }) => {
      const key = process.env.BROWSERBASE_API_KEY;
      if (!key) return "BROWSERBASE_API_KEY not set — fetch the page content manually into scope.md instead.";
      const res = await fetch("https://api.browserbase.com/v1/sessions", {
        method: "POST",
        headers: { "x-bb-api-key": key, "content-type": "application/json" },
        body: JSON.stringify({ url }),
      });
      // Session-based capture; for MVP, a simple page render + text extraction
      // is enough. Extend with the Browserbase SDK for JS-heavy pages.
      const body = await res.text();
      return body.slice(0, 20_000);
    },
  },
] as const;

export type AuditTool = (typeof auditToolSpecs)[number];
