# 🤝 Contributing to Hackfinity Platform

Thank you for your interest in contributing to the Hackfinity Platform! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/hackfinity-platform.git
   cd hackfinity-platform
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run Tests**
   ```bash
   # Backend verification
   python test_backend.py
   
   # Frontend tests (when available)
   cd frontend && npm test
   ```

## 📝 Development Guidelines

### Code Style

#### Python (Backend)
- Use **Black** for code formatting: `black .`
- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return values
- Write **docstrings** for all functions and classes
- Maximum line length: 88 characters

```python
# Example of good Python code style
from typing import List, Optional
import asyncio

async def get_sponsors(limit: Optional[int] = None) -> List[dict]:
    """
    Retrieve sponsors from the database.
    
    Args:
        limit: Maximum number of sponsors to return
        
    Returns:
        List of sponsor dictionaries
    """
    # Implementation here
    pass
```

#### JavaScript/React (Frontend)
- Use **Prettier** for code formatting: `npm run format`
- Follow **ESLint** rules: `npm run lint`
- Use **functional components** with hooks
- Use **meaningful component and variable names**
- Keep components small and focused

```javascript
// Example of good React component
import React, { useState, useCallback } from 'react';

const EmailScheduler = ({ onSchedule }) => {
  const [email, setEmail] = useState('');
  
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    onSchedule({ email, scheduledTime: new Date() });
  }, [email, onSchedule]);

  return (
    <form onSubmit={handleSubmit}>
      {/* Component JSX */}
    </form>
  );
};

export default EmailScheduler;
```

### Git Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   git checkout -b fix/bug-description
   git checkout -b docs/documentation-update
   ```

2. **Make Commits**
   ```bash
   git add .
   git commit -m "feat: add email scheduling functionality"
   ```

3. **Follow Conventional Commits**
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🧪 Testing

### Backend Testing
```bash
# Run the comprehensive backend test
python test_backend.py

# Run unit tests (when available)
python -m pytest tests/

# Check code coverage
coverage run -m pytest
coverage report
```

### Frontend Testing
```bash
# Run React tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run linting
npm run lint
```

## 📁 Project Structure

```
hackfinity-platform/
├── backend/                    # FastAPI backend
│   ├── server.py              # Main application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   └── App.css           # Styling
│   └── package.json          # Node.js dependencies
├── tests/                     # Test files
├── docs/                      # Additional documentation
└── README.md                  # Main documentation
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Operating system
   - Python/Node.js versions
   - Browser version (for frontend issues)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected behavior
   - Actual behavior

3. **Additional Context**
   - Error messages/logs
   - Screenshots (if applicable)
   - Related issues or PRs

### Bug Report Template
```markdown
**Environment:**
- OS: [e.g., Windows 10, macOS 12.0, Ubuntu 20.04]
- Python: [e.g., 3.9.2]
- Node.js: [e.g., 16.14.0]
- Browser: [e.g., Chrome 98.0]

**Description:**
Brief description of the bug.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**Additional Context:**
Any other context, logs, or screenshots.
```

## ✨ Feature Requests

When suggesting new features:

1. **Check existing issues** to avoid duplicates
2. **Provide clear use case** - why is this feature needed?
3. **Describe the solution** - how should it work?
4. **Consider alternatives** - what other approaches could work?

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.
```

## 🎯 Areas for Contribution

### High Priority
- [ ] User authentication and authorization
- [ ] Enhanced error handling and validation
- [ ] Comprehensive test coverage
- [ ] Performance optimizations
- [ ] Security improvements

### Medium Priority
- [ ] UI/UX improvements
- [ ] Additional email templates
- [ ] Enhanced analytics features
- [ ] Mobile responsiveness improvements
- [ ] Accessibility enhancements

### Documentation
- [ ] API documentation improvements
- [ ] Tutorial videos or guides
- [ ] Code examples and snippets
- [ ] Translation to other languages
- [ ] FAQ section

### DevOps/Infrastructure
- [ ] Docker improvements
- [ ] CI/CD pipeline setup
- [ ] Deployment guides
- [ ] Monitoring and logging
- [ ] Database optimization

## 📋 Pull Request Process

1. **Ensure your PR**:
   - Has a clear title and description
   - Includes tests for new functionality
   - Updates documentation if needed
   - Follows the coding standards
   - Passes all existing tests

2. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes.

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   - [ ] Performance improvement

   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added (if applicable)
   - [ ] Manual testing completed

   ## Screenshots (if applicable)
   Add screenshots for UI changes.

   ## Additional Notes
   Any additional information for reviewers.
   ```

3. **Review Process**:
   - PRs require at least one review
   - Address feedback promptly
   - Keep PRs focused and reasonably sized
   - Rebase or merge latest changes if needed

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special mentions in community updates

## 📞 Getting Help

- **GitHub Discussions** - For questions and ideas
- **GitHub Issues** - For bugs and feature requests
- **Discord Community** - For real-time chat and support

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Hackfinity Platform! 🚀
