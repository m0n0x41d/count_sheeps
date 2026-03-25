import { defineConfig } from "vite"

export default defineConfig({
    root: ".",
    base: "/edu_functional_design/",
    server: {
        fs: { allow: [".."] },
    },
    build: {
        outDir: "dist",
    },
})
