import { z } from 'zod'

export const createSessionSchema = z.object({
  browser: z.enum(['chromium', 'firefox', 'webkit']).default('chromium'),
  headless: z.boolean().default(true),
  viewport: z.object({
    width: z.number().int().positive().default(1440),
    height: z.number().int().positive().default(900),
  }).default({ width: 1440, height: 900 }),
  baseUrl: z.string().url().optional(),
})

export const openSchema = z.object({
  url: z.string().min(1),
  waitUntil: z.enum(['load', 'domcontentloaded', 'networkidle', 'commit']).default('load'),
  timeoutMs: z.number().int().positive().max(120000).default(30000),
})

export const clickSchema = z.object({
  selector: z.string().min(1),
  timeoutMs: z.number().int().positive().max(120000).default(15000),
})

export const typeSchema = z.object({
  selector: z.string().min(1),
  text: z.string(),
  clear: z.boolean().default(true),
  timeoutMs: z.number().int().positive().max(120000).default(15000),
})

export const selectSchema = z.object({
  selector: z.string().min(1),
  value: z.string().min(1),
  timeoutMs: z.number().int().positive().max(120000).default(15000),
})

export const waitForSchema = z.object({
  selector: z.string().min(1),
  state: z.enum(['attached', 'detached', 'visible', 'hidden']).default('visible'),
  timeoutMs: z.number().int().positive().max(120000).default(15000),
})

export const submitSchema = z.object({
  selector: z.string().min(1),
  timeoutMs: z.number().int().positive().max(120000).default(15000),
})

export const readSchema = z.object({
  selector: z.string().min(1),
  timeoutMs: z.number().int().positive().max(120000).default(15000),
})

export const screenshotSchema = z.object({
  path: z.string().min(1),
  fullPage: z.boolean().default(true),
})
