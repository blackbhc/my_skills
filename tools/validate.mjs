#!/usr/bin/env node

/**
 * LLM Skill 校验脚本
 *
 * 扫描 skills/ 下所有 SKILL.md，检查：
 * - 文件是否存在
 * - 元数据字段（id, description, triggers）齐全
 * - id 与目录名一致
 * - triggers 非空
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
const SKILLS_DIR = join(ROOT, "skills");

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
 * Parse metadata block from SKILL.md content.
 * Assumes the block starts after "## Metadata" heading and continues
 * as lines like "- **key**: `value`" until next heading.
 */
function parseMetadata(content, filePath) {
  const meta = {};

  // Find the Metadata section
  const metaMatch = content.match(/^## Metadata\s*\n([\s\S]*?)(?=^## )/m);
  if (!metaMatch) {
    error(`[${filePath}] 缺少 "## Metadata" 章节`);
    return meta;
  }

  const block = metaMatch[1];
  // Match backtick-wrapped values first, then plain text (until end of line or comment)
  const fieldRegex = /^- \*\*(\w+)\*\*:\s*(?:`([^`]*)`|(.+?)(?:\s*<!--.*?-->)?\s*$)/gm;
  let match;

  while ((match = fieldRegex.exec(block)) !== null) {
    // match[2] = backtick value, match[3] = plain text value
    const value = (match[2] !== undefined ? match[2] : match[3]).trim();
    if (value) {
      meta[match[1]] = value;
    }
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
  const requiredFields = ["id", "description", "triggers"];
  for (const field of requiredFields) {
    if (!meta[field] || meta[field].trim() === "") {
      error(`[${fileLabel}] 缺少必需元数据字段: ${field}`);
    }
  }

  // id should match directory name (skip for template files)
  if (meta.id && !isFile && meta.id !== label) {
    error(`[${fileLabel}] id ("${meta.id}") 与目录名 ("${label}") 不一致`);
  } else if (meta.id && !isFile) {
    pass(`[${fileLabel}] id 与目录名一致 ✓`);
  }
}

function scanSkills(baseDir) {
  if (!existsSync(baseDir)) {
    error(`skills/ 目录不存在: ${baseDir}`);
    return;
  }

  const entries = readdirSync(baseDir);
  let skillCount = 0;

  for (const entry of entries) {
    const entryPath = join(baseDir, entry);
    if (!statSync(entryPath).isDirectory()) continue;
    if (entry.startsWith(".")) continue;

    skillCount++;
    validateSingleSkill(entryPath, entry);
  }

  if (skillCount === 0) {
    error("skills/ 目录下没有 skill 子目录");
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
  scanSkills(SKILLS_DIR);
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
