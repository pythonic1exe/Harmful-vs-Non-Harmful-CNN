# Frontend — Harmful Content Detector

A **React + TypeScript** single-page application for uploading images and displaying harmful-content classification results alongside AI-generated captions.

---

## Directory Structure

```
frontend/
├── index.html
├── vite.config.ts                 # Vite build config
├── tsconfig.json                  # TypeScript project references
├── tsconfig.app.json              # App-specific TS config
├── tsconfig.node.json             # Node/tooling TS config
├── eslint.config.js               # ESLint flat config
├── package.json
├── FRONTEND.md                    # This file
└── src/
    ├── main.tsx                   # React entry point (mounts <App />)
    ├── App.tsx                    # Root component — state, upload handler, routing between views
    ├── App.css                    # All component styles
    ├── index.css                  # Global / reset styles
    ├── api.ts                     # Axios API client — talks to FastAPI backend
    ├── types.ts                   # Shared TypeScript interfaces
    └── components/
        ├── ImageUpload.tsx        # Drag-and-drop / click-to-upload input
        └── ResultDisplay.tsx      # Classification result card + caption display
```

---

## Tech Stack

| Technology      | Version | Purpose                            |
|-----------------|---------|------------------------------------|
| React           | 19      | UI framework                       |
| TypeScript      | ~5.9    | Static typing                      |
| Vite            | 7       | Dev server, bundler                |
| Axios           | 1.13    | HTTP requests to the backend       |
| ESLint          | 9       | Linting (react-hooks, react-refresh plugins) |

---

## Prerequisites

- Node.js 18+
- Backend running at `http://127.0.0.1:8000` (see [../backend/BACKEND.md](../backend/BACKEND.md))

---

## Setup & Running

```bash
# Install dependencies
npm install

# Start development server (hot reload)
npm run dev

# Type-check and build for production
npm run build

# Preview production build locally
npm run preview

# Lint the codebase
npm run lint
```

Dev server runs at `http://localhost:5173`.

---

## Application Flow

```
App (state: result, isLoading, error)
 │
 ├── [no result] → <ImageUpload />
 │       └── user selects / drops image
 │               └── calls uploadImage(file) via api.ts
 │                       └── POST /predict-with-caption → backend
 │
 └── [result ready] → <ResultDisplay />
         ├── image preview
         ├── HARMFUL / NON-HARMFUL badge
         ├── confidence percentage
         ├── AI caption (title + description)
         └── "Analyze Another Image" button → resets state
```

---

## Component Reference

### `App.tsx`
Root component. Manages three pieces of state:

| State        | Type                        | Description                          |
|--------------|-----------------------------|--------------------------------------|
| `result`     | `PredictionResponse \| null`| API response; `null` shows upload view|
| `isLoading`  | `boolean`                   | Shows loading indicator during request|
| `error`      | `string \| null`            | Error message shown above the uploader|

Key handlers:
- `handleUpload(file)` — calls the API, creates a local `objectURL` preview, stores result
- `handleReset()` — clears result and error, returns to upload view

---

### `ImageUpload.tsx`
Accepts images via click or drag-and-drop.

| Prop        | Type                    | Description                          |
|-------------|-------------------------|--------------------------------------|
| `onUpload`  | `(file: File) => void`  | Called with the selected File object |
| `isLoading` | `boolean`               | Disables input and shows overlay     |

Behaviour:
- Validates `file.type.startsWith("image/")` before calling `onUpload`
- Shows a thumbnail preview once a file is chosen
- Drag-enter/leave/over/drop events managed with `dragActive` state

---

### `ResultDisplay.tsx`
Displays the classification result returned by the API.

| Prop           | Type                  | Description                           |
|----------------|-----------------------|---------------------------------------|
| `result`       | `PredictionResponse`  | Full API response object              |
| `onReset`      | `() => void`          | Callback for the "Analyze Another" button |
| `imagePreview` | `string?`             | Local `objectURL` for the analyzed image |

Renders:
- Image preview (`<img>` from local object URL)
- Status badge — `⚠️ HARMFUL CONTENT DETECTED` (red) or `✅ SAFE CONTENT` (green)
- Confidence percentage (e.g. `87.31%`)
- Caption box with `title` and `description` (when present)
- Error message if `caption_error` is returned

---

## API Client (`api.ts`)

```typescript
const API_URL = "http://127.0.0.1:8000";

uploadImage(file: File): Promise<PredictionResponse>
```

- Sends a `multipart/form-data` POST to `/predict-with-caption`
- Returns a typed `PredictionResponse`
- Throws on HTTP error (caught in `App.tsx`)

> To change the backend URL, update `API_URL` in [src/api.ts](src/api.ts).

---

## Types (`types.ts`)

```typescript
interface PredictionResponse {
    label: "HARMFUL" | "NON_HARMFUL";    // CNN classification
    confidence: number;                   // Raw sigmoid probability (0–1)
    threshold: number;                    // Decision threshold (0.5)
    caption?: {
        title: string;                    // AI-generated title (≤ 8 words)
        description: string;              // AI-generated description (1–2 sentences)
    };
    caption_error?: string;               // Populated if captioning failed
    imagePreview?: string;                // Client-side object URL (not from API)
}
```

---

## Styling

All styles live in `src/App.css`. Key CSS classes:

| Class                  | Used in         | Description                              |
|------------------------|-----------------|------------------------------------------|
| `.app-container`       | `App`           | Centered page wrapper                    |
| `.upload-container`    | `ImageUpload`   | Upload card wrapper                      |
| `.drop-zone`           | `ImageUpload`   | Drag-and-drop target area                |
| `.drop-zone.active`    | `ImageUpload`   | Highlighted state during drag-over       |
| `.result-container`    | `ResultDisplay` | Result card wrapper                      |
| `.result-container.harmful` | `ResultDisplay` | Red accent for harmful results      |
| `.result-container.safe`    | `ResultDisplay` | Green accent for safe results       |
| `.status-badge`        | `ResultDisplay` | Prominent label (HARMFUL / SAFE)         |
| `.caption-box`         | `ResultDisplay` | AI title + description card              |
| `.reset-button`        | `ResultDisplay` | "Analyze Another Image" button           |

---

## Dependencies

### Runtime
| Package      | Version | Purpose                  |
|--------------|---------|--------------------------|
| `react`      | ^19.2.0 | UI framework             |
| `react-dom`  | ^19.2.0 | DOM rendering            |
| `axios`      | ^1.13.2 | HTTP client              |

### Dev / Build
| Package                    | Purpose                              |
|----------------------------|--------------------------------------|
| `vite`                     | Build tool and dev server            |
| `@vitejs/plugin-react`     | React fast-refresh in Vite           |
| `typescript`               | Static typing                        |
| `eslint`                   | Linting                              |
| `eslint-plugin-react-hooks`| Lint React hook rules                |
| `eslint-plugin-react-refresh` | Lint HMR compatibility           |
