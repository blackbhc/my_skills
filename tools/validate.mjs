#!/usr/bin/env node

/**
 * LLM Skill 校验脚本
 *
 * 扫描仓库根目录下所有 SKILL.md（自动跳过 .git / templates / tools / docs），检查：
 * - 文件是否存在
 * - 元数据字段（name, description）齐全
 * - name 与目录名一致
 * - description 包含 "Use when:" 触发词
 *
 * 用法：
 *   node tools/validate.mjs              # 校验全部 skill
 *   node tools/validate.mjs <path>       # 校验指定文件
 *
 * 退出码：0 = 全部通过，1 = 存在错误
 */

import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, dirname, basename, extname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

// 跳过这些非 skill 目录
const SKIP_DIRS = new Set([".git", "templates", "tools", "docs", "scripts", "node_modules"]);

let exitCode = 0;
const errors = [];
const passes = [];

function error(msg) {
  errors.push(msg);
  exitCode = 1;
}

function pass(msg) {
  passes.push(msg);
}

/**
 * Parse YAML frontmatter from SKILL.md content.
 * The frontmatter is between `---` markers at the very beginning of the file.
 * Returns a flat meta object with extracted fields.
 */
function parseMetadata(content, filePath) {
  const meta = {};

  // Match YAML frontmatter between --- markers
  const fmMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  if (!fmMatch) {
    error(`[${filePath}] 缺少 YAML frontmatter（须以 --- 开头）`);
    return meta;
  }

  const yamlBlock = fmMatch[1];
  let currentKey = null;
  let currentValue = [];

  const lines = yamlBlock.split("\n");

  for (const rawLine of lines) {
    // Skip empty lines in the middle of a value block
    const line = rawLine.trimEnd();

    // Check for top-level key: value or key: |
    const topLevelMatch = line.match(/^(\w+):\s*(.*)/);
    if (topLevelMatch) {
      // Save previous multi-line value if any
      if (currentKey && currentValue.length > 0) {
        meta[currentKey] = currentValue.join("\n").trim();
        currentValue = [];
      }

      currentKey = topLevelMatch[1];
      const rest = topLevelMatch[2];

      if (rest === "|") {
        // Multi-line value follows (indented lines)
        currentValue = [];
      } else {
        // Single-line value
        meta[currentKey] = rest.trim();
        currentKey = null;
      }
    } else if (currentKey && currentValue !== null) {
      // Continuation of multi-line value (indented with spaces)
      currentValue.push(line);
    }
  }

  // Flush last multi-line value
  if (currentKey && currentValue.length > 0) {
    meta[currentKey] = currentValue.join("\n").trim();
  }

  return meta;
}

function validateSingleSkill(skillDir, label) {
  // skillDir may be a directory (scanning skills/) or a file (specific file arg)
  const isFile = !statSync(skillDir).isDirectory();
  const skillPath = isFile ? skillDir : join(skillDir, "SKILL.md");
  const fileLabel = isFile ? basename(skillDir) : `${label}/SKILL.md`;

  // Check file exists
  if (!existsSync(skillPath)) {
    error(`[${fileLabel}] 文件不存在`);
    return;
  }

  const content = readFileSync(skillPath, "utf-8");
  const meta = parseMetadata(content, fileLabel);

  // Required fields
  const requiredFields = ["name", "description"];
  for (const field of requiredFields) {
    if (!meta[field] || meta[field].trim() === "") {
      error(`[${fileLabel}] 缺少必需元数据字段: ${field}`);
    }
  }

  // Check description contains "Use when:" for trigger words
  if (meta.description && !meta.description.includes("Use when:")) {
    error(`[${fileLabel}] description 中缺少 "Use when:" 触发词定义`);
  }

  // name should match directory name (skip for template files)
  if (meta.name && !isFile && meta.name !== label) {
    error(`[${fileLabel}] name ("${meta.name}") 与目录名 ("${label}") 不一致`);
  } else if (meta.name && !isFile) {
    pass(`[${fileLabel}] name 与目录名一致 ✓`);
  }
}

function scanSkills(baseDir) {
  if (!existsSync(baseDir)) {
    error(`根目录不存在: ${baseDir}`);
    return;
  }

  const entries = readdirSync(baseDir);
  let skillCount = 0;

  for (const entry of entries) {
    const entryPath = join(baseDir, entry);
    if (!statSync(entryPath).isDirectory()) continue;
    if (entry.startsWith(".")) continue;
    if (SKIP_DIRS.has(entry)) continue;

    // Must contain SKILL.md to be considered a skill directory
    if (!existsSync(join(entryPath, "SKILL.md"))) continue;

    skillCount++;
    validateSingleSkill(entryPath, entry);
  }

  if (skillCount === 0) {
    error("未找到任何包含 SKILL.md 的 skill 目录");
  } else {
    pass(`共扫描 ${skillCount} 个 skill 目录 ✓`);
  }
}

// --- Main ---

// Check if a specific file was provided
const specificFile = process.argv[2];

if (specificFile) {
  const fullPath = join(process.cwd(), specificFile);
  const dirName = basename(dirname(fullPath));
  const fileName = basename(fullPath);

  if (!existsSync(fullPath)) {
    error(`文件不存在: ${fullPath}`);
  } else if (extname(fullPath) !== ".md") {
    error(`不是 Markdown 文件: ${fullPath}`);
  } else {
    // Named SKILL.md → validate as skill directory; otherwise validate the file directly
    const skillDir = fileName === "SKILL.md" ? dirname(fullPath) : fullPath;
    validateSingleSkill(skillDir, fileName === "SKILL.md" ? dirName : fileName);
  }
} else {
  scanSkills(ROOT);
}

// --- Report ---

console.log("\n📋 LLM Skill 校验报告\n");

if (passes.length > 0) {
  console.log("✅ 通过：");
  passes.forEach((p) => console.log(`   ${p}`));
}

if (errors.length > 0) {
  console.log("❌ 错误：");
  errors.forEach((e) => console.log(`   ${e}`));
}

console.log(`\n结果：${passes.length} 通过，${errors.length} 错误`);

process.exit(exitCode);
