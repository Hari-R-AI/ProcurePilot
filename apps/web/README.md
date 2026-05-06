# ProcurePilot Frontend
Next.js AI Procurement Copilot MVP

## Quick Start

### 1. Install Dependencies

```bash
cd apps/web
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local` and set the backend URL:

```bash
cp .env.example .env.local
```

Update `NEXT_PUBLIC_API_BASE_URL` in `.env.local`:
- Local dev: `http://localhost:8000`
- Remote: `https://api.example.com`

### 3. Run Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

- `app/` — Next.js App Router pages
  - `layout.tsx` — Root layout
  - `page.tsx` — Landing page
  - `dashboard/page.tsx` — Main analysis UI
- `components/` — Reusable React components
  - `procurement-request-form.tsx` — Request submission form
  - `recommendation-panel.tsx` — Analysis results display
  - `policy-snippets.tsx` — Policy display
  - `risk-flags.tsx` — Risk visualization
  - Common components (header, footer, etc.)
- `services/` — API client and data fetching
  - `api.ts` — Backend API client
- `types/` — TypeScript type definitions
  - `procurement.ts` — Procurement-related types
- `lib/` — Utility functions
  - `utils.ts` — Helper functions
- `styles/` — Global styles
  - `globals.css` — Tailwind & global styles
- `public/` — Static assets

## Environment Variables

See `.env.example` for all available options.

Key variables:
- `NEXT_PUBLIC_API_BASE_URL` — Backend API URL (required)

## API Client

The `services/api.ts` provides a typed API client:

```typescript
import { api } from "@/services/api";

// Analyze procurement request
const response = await api.procurement.analyze({
  title: "...",
  description: "...",
  // ...
});
```

## Types

Frontend types are aligned with backend schemas:

```typescript
import type { 
  ProcurementRequest, 
  AnalysisResponse,
  Requirement,
  PolicyChunk,
  RiskFlag,
  RecommendationItem 
} from "@/types/procurement";
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect to Vercel
3. Set `NEXT_PUBLIC_API_BASE_URL` in environment variables
4. Deploy

```bash
vercel deploy
```

### Docker

```bash
docker build -t procurepilot-web:latest .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://api:8000 \
  procurepilot-web:latest
```

### Manual Deployment

```bash
npm run build
npm run start
```

Server will listen on port 3000.

## Development

### Type Checking

```bash
npm run type-check
```

### Formatting

```bash
npm run format
```

### Linting

```bash
npm run lint
```

## Component Patterns

All components use React functional components with TypeScript:

```typescript
interface ComponentProps {
  // Props
}

export default function Component({ /* props */ }: ComponentProps) {
  return (
    // JSX
  );
}
```

## API Response Handling

API responses include trace IDs for debugging:

```typescript
const response = await api.procurement.analyze(...);
console.log(response.request_id);  // Track requests
console.log(response.trace_id);    // Trace through system
```

## Styling

Uses Tailwind CSS for styling. Custom colors defined in `tailwind.config.ts`:

- `primary` — Main brand color
- `success` — Success states
- `warning` — Warning states
- `danger` — Error states

## Testing (Future)

Integration tests with backend will be added in Phase 6.

## Troubleshooting

### API Connection Error

1. Ensure backend is running: `uvicorn app.main:app --reload`
2. Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
3. Verify CORS is configured in backend

### Build Errors

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Port 3000 Already in Use

```bash
npm run dev -- -p 3001
```
