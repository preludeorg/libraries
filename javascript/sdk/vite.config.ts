/// <reference types="vitest" />

import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, "lib/main.ts"),
      name: "@theprelude/sdk",
      fileName: "sdk",
    },
    rollupOptions: {},
  },
  test: {
    testTimeout: 30_000,
    setupFiles: ["./test/setup.ts"],
  },
});
