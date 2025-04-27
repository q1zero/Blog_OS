## Development Guidelines

### Framework and Language
> Analyze the framework and language choices for this project, focusing on best practices and standardization.

**Framework Considerations:**
- Version Compatibility: Ensure all dependencies are compatible with the chosen framework version
- Feature Usage: Leverage framework-specific features rather than reinventing solutions
- Performance Patterns: Follow recommended patterns for optimal performance
- Upgrade Strategy: Plan for future framework updates with minimal disruption
- Importance Notes for Framework:
	* Django 4.2.20: 官方 LTS 版本，社区活跃，稳定性高
	* djangorestframework 3.14.x: 用于实现 RESTful API
	* mysqlclient 2.2.0: MySQL 数据库驱动
	* djangorestframework-simplejwt: 用于 JWT 认证和权限管理

**Language Best Practices:**
- Type Safety: Use strong typing where available to prevent runtime errors
- Modern Features: Utilize modern language features while maintaining compatibility
- Consistency: Apply consistent coding patterns throughout the codebase
- Documentation: Document language-specific implementations and workarounds

### Code Abstraction and Reusability
> During development, prioritize code abstraction and reusability to ensure modular and component-based functionality. Try to search for existing solutions before reinventing the wheel.
> List below the directory structure of common components, utility functions, and API encapsulations in the current project.


**Modular Design Principles:**
- Single Responsibility: Each module is responsible for only one functionality
- High Cohesion, Low Coupling: Related functions are centralized, reducing dependencies between modules
- Stable Interfaces: Expose stable interfaces externally while internal implementations can vary

**Reusable Component Library:**
```
root
- .venv               // 虚拟环境目录
- pyproject.toml      // 项目依赖配置
- blog                // Django 项目目录
    - manage.py       // Django 管理命令入口
    - apps            // 应用模块目录
        - users       // 用户管理模块
        - articles    // 文章管理模块
        - comments    // 评论模块
    - config          // 项目配置（settings, urls, wsgi, asgi）
    - utils           // 通用工具函数
- plan.md             // 项目开发计划
- README.md           // 项目说明文档
- uv.lock             // 锁文件
```

### Coding Standards and Tools
**Code Formatting Tools:**
- [ESLint (version)]() // JavaScript/TypeScript code checking
- [Prettier (version)]() // Code formatting
- [StyleLint (version)]() // CSS/SCSS code checking

**Naming and Structure Conventions:**
- Naming Style: Python 使用 snake_case, 类名使用 PascalCase
- Module/Package: 使用功能相关划分，模块间低耦合

### Frontend-Backend Collaboration Standards
**API Design and Documentation:**
- RESTful design principles
	* Use HTTP methods (GET, POST, PUT, DELETE) to represent operations
	...
- Timely interface documentation updates
	* Document API endpoints, parameters, and responses
	...
- Unified error handling specifications
	...
	

**Data Flow:**
- Clear frontend state management
	* Use a state management library (e.g., Redux, Pinia) for consistent state handling
	...
- Data validation on both frontend and backend
	* Validate data types and constraints
	...
- Standardized asynchronous operation handling
	* Use consistent API call patterns
	...

### Performance and Security
**Performance Optimization Focus:**
- Resource loading optimization
	* Use code splitting and lazy loading
	...
- Rendering performance optimization
	* Use virtualization and pagination for large lists
	...
- Appropriate use of caching
	* Implement caching strategies for API responses
	...

**Security Measures:**
- Input validation and filtering
	* Validate user inputs and sanitize data
	...
- Protection of sensitive information
	* Use secure authentication and authorization mechanisms
	...
- Access control mechanisms
	* Implement role-based access control
	...