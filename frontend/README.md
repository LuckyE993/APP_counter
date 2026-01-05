# Beancount Accounting App - Frontend

Vue 3 PWA frontend for intelligent accounting with VLM-powered bill recognition.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

4. Preview production build:
```bash
npm run preview
```

## Features

- PWA support (installable, offline-capable)
- Image upload with camera access
- Text-based quick entry
- Transaction editing
- Balance view
- Mobile-optimized responsive design

## Configuration

The frontend proxies API requests to `http://localhost:8000` in development mode. Update `vite.config.js` if your backend runs on a different port.
