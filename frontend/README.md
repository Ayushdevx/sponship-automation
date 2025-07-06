# 🎨 Hackfinity Platform - Frontend

> **React-based frontend for the Hackfinity certificate and sponsorship automation platform with modern UI/UX, drag & drop interfaces, and real-time analytics.**

[![React](https://img.shields.io/badge/react-19.0-blue.svg)](https://reactjs.org)
[![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org)
[![Tailwind CSS](https://img.shields.io/badge/tailwind-css-blue.svg)](https://tailwindcss.com)

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+**
- **npm** (comes with Node.js)
- Backend server running on `http://localhost:8000`

### Installation & Setup

```bash
# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm start
```

The application will open at `http://localhost:3000` (or next available port).

## 🏗️ Project Structure

```
frontend/
├── 📁 public/                 # Static assets
│   ├── index.html            # HTML template
│   ├── manifest.json         # PWA manifest
│   └── robots.txt            # SEO configuration
│
├── 📁 src/                   # React source code
│   ├── App.js               # Main application component
│   ├── App.css              # Global styles and themes
│   ├── index.js             # React entry point
│   └── index.css            # Base styles
│
├── 📄 package.json           # Dependencies and scripts
├── 📄 tailwind.config.js     # Tailwind CSS configuration
├── 📄 postcss.config.js      # PostCSS configuration
└── 📄 craco.config.js        # CRACO configuration
```

## ⚙️ Available Scripts

### Development

```bash
# Start development server with hot reload
npm start
```
- Runs the app in development mode
- Opens http://localhost:3000 in your browser
- Page reloads automatically when you make changes
- Lint errors appear in the console

### Testing

```bash
# Run test suite in watch mode
npm test
```
- Launches the test runner in interactive watch mode
- Tests run automatically when files change
- See [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information

### Production Build

```bash
# Create optimized production build
npm run build
```
- Builds the app for production to the `build` folder
- Optimizes React in production mode for best performance
- Build is minified and filenames include hashes
- Ready for deployment!

### Code Quality

```bash
# Eject from Create React App (irreversible)
npm run eject
```
**⚠️ Warning: This is a one-way operation. Once you eject, you can't go back!**

## 🎨 Features

### Core UI Components

- **📊 Interactive Dashboard**: Real-time analytics with multiple chart types
- **📁 Drag & Drop Upload**: Intuitive file upload with progress indicators
- **📧 Email Scheduler**: Visual interface for scheduling campaigns
- **🎨 Template Designer**: Visual editor for email and certificate templates
- **📱 Responsive Design**: Mobile-first approach with Tailwind CSS

### Advanced Features

- **🔄 Real-time Updates**: Live status updates via WebSocket connections
- **📈 Data Visualization**: Charts using Chart.js, Recharts, and Plotly.js
- **🎯 Interactive Elements**: Drag & drop, color pickers, and rich text editors
- **🔒 Secure File Handling**: Client-side validation and secure upload
- **⚡ Performance Optimized**: Code splitting and lazy loading

## 🛠️ Technology Stack

### Core Technologies

- **React 19.0**: Latest React with concurrent features
- **Create React App**: Bootstrap and build tooling
- **CRACO**: Custom configuration without ejecting

### UI Libraries & Styling

- **Tailwind CSS**: Utility-first CSS framework
- **React Modal**: Accessible modal dialogs
- **React Color**: Color picker components
- **React Select**: Enhanced select components

### Data Visualization

- **Chart.js**: Canvas-based charts
- **React Chart.js 2**: React wrapper for Chart.js
- **Recharts**: SVG-based charts built on D3
- **Plotly.js**: Scientific and statistical charts
- **React Plotly.js**: React bindings for Plotly

### File & Data Handling

- **Axios**: HTTP client for API communication
- **React DnD**: Drag and drop functionality
- **HTML2Canvas**: Screenshot generation
- **jsPDF**: PDF generation
- **Lodash**: Utility functions

### Development Tools

- **React Router DOM**: Client-side routing
- **React Ace**: Code editor component
- **Moment.js**: Date manipulation
- **UUID**: Unique identifier generation

## 🌐 API Integration

The frontend communicates with the FastAPI backend through RESTful APIs:

### Base Configuration

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Key Endpoints

- `POST /upload-participants` - Upload participant CSV
- `POST /upload-sponsors` - Upload sponsor CSV  
- `POST /schedule-emails` - Schedule email campaigns
- `GET /analytics` - Fetch analytics data
- `POST /generate-certificates` - Generate certificates

## 🎨 Styling & Theming

### Tailwind CSS Configuration

The app uses Tailwind CSS for styling with custom configuration:

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
        // Custom color palette
      }
    }
  }
}
```

### Custom Styles

Additional styles are defined in:
- `src/App.css` - Component-specific styles
- `src/index.css` - Global base styles

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Static Hosting

The build folder can be deployed to:
- **Netlify**: Drag & drop deployment
- **Vercel**: Git-based deployment
- **GitHub Pages**: Free hosting for public repos
- **AWS S3**: Static website hosting
- **Firebase Hosting**: Google's hosting platform

### Environment Variables

Create `.env` file for environment-specific configuration:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

## 🧪 Testing

### Test Structure

```bash
src/
├── __tests__/          # Test files
├── components/         # Component tests
└── utils/             # Utility function tests
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- --testNamePattern="App"
```

## 🔧 Development Tips

### Performance Optimization

- Use React.memo for expensive components
- Implement code splitting with React.lazy
- Optimize images and assets
- Use production build for deployment

### Debugging

- React Developer Tools browser extension
- Console.ninja extension for enhanced debugging
- Network tab for API request debugging

### Code Style

- Use ESLint for code linting
- Follow React best practices
- Implement proper error boundaries
- Use TypeScript for type safety (future enhancement)

## 🤝 Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/new-component`
2. Make changes and test thoroughly
3. Follow component naming conventions
4. Update tests if needed
5. Submit pull request

### Component Guidelines

- Use functional components with hooks
- Implement proper prop validation
- Follow naming conventions (PascalCase for components)
- Include JSDoc comments for complex functions

## 📚 Learning Resources

- [React Documentation](https://reactjs.org/)
- [Create React App Documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

## ❓ Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 3000
npx kill-port 3000
```

**Node modules issues:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**Build fails:**
```bash
# Increase Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

---

**🔗 Related**: [Backend Documentation](../backend/README.md) | [Main Project README](../README.md)
