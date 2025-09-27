# Mintair - One Click Blockchain Infrastructure

A modern, responsive single-page application inspired by Mintair, built with Next.js 15 and Tailwind CSS. Mintair provides a sleek interface for blockchain node deployment services with a dark, ocean-themed design.

## Features

-   **Modern Design**: Dark theme with ocean and neon color palette
-   **Responsive Layout**: Mobile-first design that works on all devices
-   **Interactive Components**: Hover effects, animations, and smooth transitions
-   **Component-Based Architecture**: Reusable React components
-   **TypeScript Support**: Full type safety throughout the application

## Tech Stack

-   **Framework**: Next.js 15 with App Router
-   **Styling**: Tailwind CSS 4 with custom color palette
-   **Icons**: Lucide React
-   **Animations**: Custom CSS animations and Tailwind utilities
-   **TypeScript**: Full type safety

## Project Structure

```
src/
├── app/
│   ├── globals.css          # Global styles and theme
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page component
├── components/
│   ├── common/
│   │   ├── header.tsx       # Navigation header
│   │   └── footer.tsx       # Footer component
│   └── landing/
│       ├── hero.tsx         # Hero section
│       ├── how-it-works.tsx # How it works section
│       ├── features.tsx     # Features showcase
│       ├── chains.tsx       # Supported chains
│       └── community.tsx     # Community section
└── lib/
    └── utils.ts             # Utility functions
```

## Getting Started

1. Install dependencies:

    ```bash
    npm install
    ```

2. Run the development server:

    ```bash
    npm run dev
    ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Design System

### Color Palette

-   **Ocean**: Blue gradient colors for primary elements
-   **Neon**: Green gradient colors for accents
-   **Dark**: Dark background colors for depth
-   **Electric**: Additional blue tones for variety

### Typography

-   **Primary Font**: Geist Sans
-   **Monospace Font**: Geist Mono
-   **Fallback**: Inter, Arial, Helvetica

### Components

-   **Header**: Fixed navigation with mobile menu
-   **Hero**: Full-screen landing section with CTA
-   **How It Works**: 3-step process explanation
-   **Features**: 6 feature cards with icons
-   **Chains**: Interactive chain selection grid
-   **Community**: Social links and testimonials
-   **Footer**: Comprehensive footer with links

## Customization

The design system is easily customizable through:

1. **Colors**: Modify the color palette in `globals.css`
2. **Components**: Update individual component files
3. **Content**: Change text and data in component files
4. **Animations**: Adjust CSS animations in `globals.css`

## Deployment

The application is ready for deployment on platforms like Vercel, Netlify, or any other Next.js-compatible hosting service.

## License

This project is for demonstration purposes and showcases modern web development practices with Next.js and Tailwind CSS.
