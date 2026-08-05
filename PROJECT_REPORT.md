# 2GOI URL Shortener — Complete Academic Project Report

## Cover Page

**Project Title:** 2GOI — A Production-Grade URL Shortener with Analytics

**Submitted by:** Badri Pamisetty

**Project Type:** Full-Stack Web Application

**Live URL:** https://2goi.in

**GitHub Repository:** https://github.com/Badri-2915/2goi

**Technologies Used:** React, FastAPI, PostgreSQL, Redis, Supabase, Docker, Render

## Table of Contents

1. Abstract
2. Introduction
3. Problem Statement
4. Objectives
5. Literature Survey
6. System Requirements
7. System Architecture and Design
8. Database Design
9. Detailed Module Descriptions
10. API Design
11. Authentication System
12. URL Shortening Algorithm (Base62)
13. Caching Strategy (Redis)
14. Click Analytics Engine
15. Frontend Design
16. Workflow and Data Flow
17. Deployment and DevOps
18. Challenges Faced and Solutions
19. Scalability and World-Wide Challenges
20. Fault Tolerance and Failover
21. Security Analysis
22. Performance Analysis
23. Testing
24. SEO and Discoverability
25. Email System
26. Cost Analysis
27. Future Enhancements
28. Comparison with Existing Solutions
29. Conclusion
30. References
31. Appendix A: Complete Code Walkthrough
32. Appendix B: Environment Variables
33. Appendix C: Database Schema SQL
34. Appendix D: API Documentation
35. Appendix E: Glossary of Terms
36. Appendix F: Interview Questions and Answers (Resume Preparation)
37. Appendix G: Resume Bullet Points
38. Appendix H: Real Code from the Repository
39. Appendix I: How to Explain This Project in an Interview (Script)
40. Appendix J: Complete Project Folder Structure
41. Appendix K: Design Patterns Used in This Project
42. Appendix L: Step-by-Step Feature Walkthroughs
43. Appendix M: Entity-Relationship Diagram
44. Appendix N: Sequence Diagrams
45. Appendix O: Additional Interview Questions (Advanced)
46. Appendix P: Project Timeline
47. Appendix Q: Key Metrics and Numbers


# 1. Abstract

2GOI is a production-grade URL shortener built as a full-stack web application. It converts long, unwieldy URLs into short, shareable links. For example, a long URL like `https://www.google.com/search?q=url+shortener+project&oq=url+shortener&gs_lcp=Cgdnd3Mtd2l6EAM` becomes `https://2goi.in/2Bi`. When someone clicks a short link, they are instantly redirected to the original destination URL.

The project goes beyond a simple URL shortener by incorporating several production-level features. It uses Base62 encoding from sequential database IDs, which guarantees zero collisions and eliminates the need for duplicate-checking queries. It uses Redis caching with the cache-aside pattern, which delivers sub-5-millisecond redirect response times. Click analytics are logged asynchronously so they never slow down the redirect. Daily statistics are pre-aggregated using PostgreSQL's upsert (INSERT ON CONFLICT) pattern. Every shortened link gets a QR code. Users can set custom aliases and link expiration times. Authentication supports both Google OAuth and email/password via Supabase. Rate limiting prevents abuse.

The project uses a single-domain architecture where the frontend, API, and redirect service all run on one domain (2goi.in) in a single Docker container. It is deployed in production on Render with a custom domain, SSL certificates, and auto-deployment from GitHub. The entire infrastructure runs on free tiers, costing approximately 67 rupees per month (domain registration only).

This report covers every aspect of the project in detail: the motivation behind building it, the architectural decisions, the algorithms used, the challenges encountered during development, how we solved those challenges, and how the system could scale to handle millions of users worldwide.


# 2. Introduction

## 2.1 What is a URL Shortener?

A URL shortener is a web service that converts long URLs into short, easy-to-share links. When someone clicks the short URL, the service looks up the original URL in its database and redirects the user to the destination. This entire process happens in milliseconds.

Consider this example. A long URL like this:

```
https://www.amazon.in/dp/B09V3KXJPB/ref=cm_sw_r_cp_api_i_dl_6ZRQY8XFXZJHV9KQ5CJ0?encoding=UTF8&psc=1
```

Becomes a short URL like this:

```
https://2goi.in/2Bi
```

Both URLs take the user to the same destination. But the short URL is easier to share, easier to remember, easier to type, and takes less space in messages.

URL shorteners are used in many real-world scenarios:

**Social media:** Twitter/X has character limits. A tweet has 280 characters, and a long URL could consume half of that space. Short URLs save characters for the actual message.

**Marketing:** Marketers create different short links for different campaigns (email, social media, print ads). By tracking clicks on each link separately, they can measure which campaign drives the most traffic.

**Print media:** If you see a URL on a business card, poster, or magazine ad, it needs to be short enough to type by hand. Nobody will type a 200-character URL from a poster.

**QR codes:** QR codes encode data as a pattern of black and white squares. More data means more squares, which means a more complex QR code that is harder to scan. Short URLs produce simpler QR codes.

**SMS messages:** Text messages have character limits (160 characters for SMS). Short URLs are essential for including links in text messages.

**Analytics:** When you share a regular URL, you have no way to know how many people clicked it. A URL shortener tracks every click, giving you data about who clicked, when they clicked, what device they used, and where they were located.

## 2.2 Why Build a URL Shortener?

Building a URL shortener is one of the most popular system design interview questions at companies like Google, Amazon, Meta, and Microsoft. It is an excellent project because it touches on many important computer science and software engineering concepts:

**System Design:** How do you design a system that can handle millions of redirects per day? How do you ensure every short code is unique? How do you handle hot links (links that get thousands of clicks per second)?

**Database Design:** How do you structure tables so that both writes (creating links) and reads (looking up links) are fast? How do you aggregate analytics without scanning millions of rows?

**Caching:** How does Redis achieve sub-millisecond response times? What happens when the cache is full? What happens when Redis goes down?

**Encoding Algorithms:** How does Base62 encoding work? Why do companies like Bitly and YouTube use it? How many unique codes can you generate?

**Authentication:** How do JWT tokens work? What is the difference between symmetric (HS256) and asymmetric (ES256) token verification? How does OAuth work?

**API Design:** What makes a good RESTful API? How do you handle pagination, validation, and error responses?

**DevOps:** How do you containerize an application with Docker? How do you set up auto-deployment from GitHub? How do you configure DNS and SSL?

This project demonstrates all of these concepts in a single, cohesive application that is actually deployed and running in production. It is not just a theoretical exercise — it is a real system serving real users at https://2goi.in.

## 2.3 Project Name: 2GOI

The name "2GOI" stands for "To Go I" — as in "I want to go to this URL." The `.in` domain makes the full address `2goi.in`, which reads as "to go in." The name is short (4 characters), memorable, and directly relates to the service's purpose: taking users to their desired destination.

## 2.4 Scope of the Project

This project covers the following areas:

**Frontend:** A responsive single-page application (SPA) built with React 19, Vite (build tool), and TailwindCSS (styling). It includes pages for URL shortening, user dashboard, analytics visualization, login, and signup.

**Backend:** A RESTful API built with FastAPI (Python). It handles URL shortening, redirects, user authentication, analytics, and serves the frontend static files.

**Database:** PostgreSQL hosted on Supabase. It stores links, clicks, users, and pre-aggregated analytics.

**Cache:** Redis for high-speed redirect lookups and temporary data storage.

**Authentication:** Email/password registration and login, plus Google OAuth (Login with Google), powered by Supabase Auth.

**Analytics:** Click tracking that records country, browser, device type, and referrer for every click. Daily trends are displayed as charts.

**Deployment:** Dockerized deployment on Render with auto-deploy from GitHub, custom domain (2goi.in), and automatic SSL certificates.

**SEO:** Meta tags, Open Graph tags, sitemap, robots.txt, and Google Search Console integration for search engine discoverability.

**Email:** Transactional emails (signup confirmation, password reset) via Resend SMTP integrated with Supabase Auth.


# 3. Problem Statement

## 3.1 The Problem

Long URLs are a widespread problem in modern digital communication. Here are the specific issues:

**They are ugly and unreadable.** A URL with query parameters, UTM tracking codes, session IDs, and long paths can easily be 200 or more characters long. When you paste such a URL into a message, it looks messy and unprofessional.

**They break in emails and messages.** Many email clients and messaging apps wrap long URLs across multiple lines. When the recipient clicks the wrapped URL, it often breaks because only the first line is treated as the link. This leads to "page not found" errors and frustrated users.

**They are impossible to share verbally.** Imagine trying to tell someone a URL over a phone call: "Go to h-t-t-p-s colon slash slash w-w-w dot amazon dot in slash d-p slash capital-B zero nine capital-V three..." Nobody does this because it is impractical.

**They do not fit in print.** Business cards, posters, flyers, and magazine advertisements have limited space. A long URL simply will not fit, and even if it does, nobody will bother typing it.

**They waste QR code density.** QR codes encode data as a pattern of black and white squares. The more characters in the URL, the more squares are needed, making the QR code more complex and harder to scan — especially at a distance or on small surfaces.

**They lack analytics.** If you share a regular URL, you have no idea how many people clicked it. You do not know which country they are from, what device they used, or when they clicked. This information is crucial for marketers, businesses, and content creators.

## 3.2 The Solution

Build a URL shortener that addresses all of these problems:

1. **Converts long URLs to short ones** using an efficient encoding algorithm that guarantees uniqueness
2. **Redirects fast** with sub-5-millisecond response times using Redis caching
3. **Tracks clicks** with country, browser, device type, referrer, and daily trends
4. **Generates QR codes** for every shortened link automatically
5. **Supports custom aliases** so users can create memorable short links like `2goi.in/myresume`
6. **Supports link expiration** so links can automatically become inactive after a set time
7. **Is secure** with JWT authentication, rate limiting, and input validation
8. **Is production-ready** deployed with Docker, custom domain, SSL, and auto-deployment

## 3.3 Target Users

**Students:** Sharing assignment links, project demos, and portfolio URLs with professors and classmates.

**Marketers:** Creating separate short links for different marketing campaigns (email newsletter, Instagram post, Twitter ad) to track which channel performs best.

**Businesses:** Creating branded short links for products, landing pages, and customer communications.

**Developers:** Sharing API endpoints, documentation links, and GitHub repositories in a concise format.

**Content creators:** Sharing links on social media platforms where character limits exist, while tracking how many followers actually click through.

**General users:** Anyone who needs to share a long URL in a short, clean format.


# 4. Objectives

## 4.1 Primary Objectives

1. Design and develop a full-stack URL shortening web application that is deployed and accessible on the internet
2. Implement an efficient, collision-free short code generation algorithm using Base62 encoding from sequential database IDs
3. Build a high-performance redirect system with sub-5-millisecond response times using Redis caching
4. Provide comprehensive click analytics including country, browser, device, and daily click trends displayed as visual charts
5. Deploy the application in production with a custom domain, SSL certificate, and auto-deployment from GitHub

## 4.2 Secondary Objectives

1. Implement user authentication with both email/password and Google OAuth
2. Support custom aliases so users can choose their own short codes
3. Support link expiration so links can automatically become inactive
4. Generate QR codes for every shortened link
5. Implement rate limiting to prevent abuse (100 requests/minute for anonymous users, 1000 for authenticated)
6. Optimize database queries using pre-aggregated daily click statistics
7. Set up transactional emails for signup confirmation using a custom domain email address
8. Make the site discoverable on Google Search through proper SEO practices

## 4.3 Learning Objectives

Through this project, we aimed to learn and demonstrate understanding of:

1. How to design systems that can conceptually handle millions of requests (system design thinking)
2. How caching works in real applications and why Redis is used for this purpose
3. How encoding algorithms like Base62 are used in production systems like Bitly and YouTube
4. How JWT (JSON Web Token) authentication works, including both symmetric (HS256) and asymmetric (ES256) verification
5. How OAuth 2.0 flows work, specifically the Google OAuth integration
6. How to containerize applications with Docker and deploy them to cloud platforms
7. How to configure DNS records, SSL certificates, and custom domains
8. How to integrate and orchestrate multiple third-party services (Supabase, Redis, Resend, Google Cloud, Render, UptimeRobot)
9. How to monitor application uptime and prevent cold starts on free hosting tiers using external health ping services


# 5. Literature Survey

## 5.1 Existing URL Shorteners

### Bitly (bit.ly)

Bitly is the most well-known URL shortener, founded in 2008. It handles billions of links and is used by major brands worldwide. Bitly uses a Base62-like encoding system for generating short codes. It offers features like custom domains, branded links, an analytics dashboard, and a comprehensive API. The free tier is limited, with paid plans starting from $29/month. Bitly demonstrates that URL shortening is a real business with significant market demand.

### TinyURL (tinyurl.com)

TinyURL is one of the oldest URL shorteners, founded in 2002. It has a simple, monolithic architecture and offers basic shortening with optional custom aliases. TinyURL was one of the first services to prove that URL shortening is a useful web utility, and it is still active today.

### Rebrandly (rebrandly.com)

Rebrandly focuses on branded links, allowing businesses to use their own custom domains for short links. For example, instead of `bit.ly/abc123`, a company could use `brand.co/abc123`. This focus on branding shows an evolution in the URL shortening market toward enterprise features.

### Short.io

Short.io is a white-label URL shortening solution for businesses. It provides custom domains, link analytics, and team management. It represents the B2B (business-to-business) side of the URL shortening market.

## 5.2 Common Approaches to URL Shortening

### Approach 1: Random String Generation

This approach generates a random 6-character string (like "aB3xYz") and checks if it already exists in the database. If it does, a new random string is generated and checked again.

**How it works:**
```
1. Generate random string: "aB3xYz"
2. Query database: SELECT * FROM links WHERE short_code = 'aB3xYz'
3. If exists → go to step 1
4. If not exists → save to database
```

**Advantages:**
- Simple to implement
- Short codes are unpredictable (hard to guess)

**Disadvantages:**
- Collision risk grows as the database fills up
- Due to the birthday paradox, after about 300,000 links in a 62^6 space, there is a 1% chance of collision on each generation
- After 7.5 million links, there is a 50% chance of collision
- Each collision requires an additional database query (retry)
- Under high load, multiple retries can degrade performance significantly

### Approach 2: Hashing (MD5 or SHA-256)

This approach hashes the original URL using a hash function like MD5 or SHA-256, then takes the first 6 characters of the hash as the short code.

**How it works:**
```
1. Hash the URL: MD5("https://example.com") = "d41d8cd98f00b204e980..."
2. Take first 6 characters: "d41d8c"
3. Save to database
```

**Advantages:**
- Deterministic (same URL always produces the same code)
- No database check needed (in theory)

**Disadvantages:**
- Different URLs can produce the same 6-character prefix (hash collision)
- The same URL always produces the same code (cannot shorten the same URL twice with different codes)
- Must still handle collisions

### Approach 3: Counter-Based (Base62 Encoding) — Our Approach

This approach maintains a global counter (10000, 10001, 10002...) and converts each number to a Base62 string.

**How it works:**
```
1. Insert record into database, get sequence_id = 10008
2. Encode to Base62: 10008 → "2Bq"
3. Update the record with short_code = "2Bq"
```

**Advantages:**
- Zero collisions (every sequential number is unique, so every code is unique)
- Zero extra database queries for collision checking
- Predictable capacity (we know exactly how many codes each character length supports)
- Used by the largest URL shorteners in the world (Bitly, YouTube for video IDs)
- Extremely fast (one mathematical operation)

**Disadvantages:**
- Codes are sequential and therefore predictable (someone could guess the next code)
- This predictability is not a security concern for URL shorteners because short URLs are meant to be shared publicly

**We chose Approach 3** because it is the most efficient, most reliable, and most widely-used method in production URL shortening systems.

## 5.3 Comparison of Approaches

| Criteria | Random String | Hashing | Base62 (Our Choice) |
|----------|--------------|---------|---------------------|
| Collision risk | High (grows over time) | Medium (hash prefix collisions) | Zero |
| Extra DB queries | 1-3 per collision | 1 per collision | 0 |
| Predictability | Unpredictable | Deterministic | Sequential |
| Capacity | Limited by retry overhead | Limited by prefix length | 56+ billion (6 chars) |
| Used by | Simple hobby projects | Some web apps | Bitly, YouTube, TinyURL |
| Performance at scale | Degrades | Stable | Stable |

## 5.4 Key Technologies Studied

| Technology | Category | Why We Chose It |
|-----------|----------|----------------|
| React 19 | Frontend framework | Component-based architecture, virtual DOM for performance, massive ecosystem with thousands of libraries |
| Vite | Build tool | 10-100x faster than Webpack, instant hot module replacement during development |
| TailwindCSS | CSS framework | Utility-first approach means no CSS files to maintain, highly customizable, small bundle size |
| FastAPI | Backend framework | Native async support (critical for our architecture), automatic Swagger documentation, Pydantic validation |
| SQLAlchemy | ORM | The most popular Python ORM, supports async operations, type-safe queries, migration support |
| PostgreSQL | Database | Most advanced open-source database, supports sequences, upsert, JSON, full-text search, and is free on Supabase |
| Redis | Cache | Sub-millisecond reads and writes, perfect for caching URL lookups, supports TTL for auto-expiry |
| Docker | Containerization | Consistent environments across development and production, multi-stage builds for smaller images |
| Supabase | Backend-as-a-Service | Free PostgreSQL hosting, built-in authentication with JWT, Google OAuth support, JWKS endpoint for token verification |
| Render | Cloud hosting | Free Docker deployment, auto-deploy from GitHub, free Redis, free SSL certificates |
# 6. System Requirements

## 6.1 Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01 | Users shall be able to shorten URLs without creating an account | High |
| FR-02 | Users shall be able to create accounts with email and password | High |
| FR-03 | Users shall be able to sign in with Google OAuth | High |
| FR-04 | Clicking a short URL shall redirect to the original URL | High |
| FR-05 | The system shall generate QR codes for every short link | Medium |
| FR-06 | Users shall be able to set custom aliases for short links | Medium |
| FR-07 | Users shall be able to set expiration times for links | Medium |
| FR-08 | Authenticated users shall see a dashboard of their links | High |
| FR-09 | Users shall be able to view click analytics for their links | High |
| FR-10 | Users shall be able to delete their links | Medium |
| FR-11 | The system shall track click metadata (country, browser, device) | High |
| FR-12 | The system shall display analytics as visual charts | Medium |

## 6.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01 | Redirect response time | Less than 50ms (cache hit: less than 5ms) |
| NFR-02 | System availability | 99.9% uptime (achieved via UptimeRobot health pings preventing Render cold starts) |
| NFR-03 | Concurrent users | Support 100+ simultaneous users |
| NFR-04 | Short code capacity | Support 56+ billion unique URLs |
| NFR-05 | Security | JWT authentication, rate limiting, input validation |
| NFR-06 | Mobile responsive | Work on all screen sizes |
| NFR-07 | Page load time | Less than 3 seconds on 3G connection |

## 6.3 Hardware Requirements (Development)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Processor | Dual-core 2GHz | Quad-core 3GHz or better |
| RAM | 4 GB | 8 GB or more |
| Storage | 10 GB free space | 20 GB or more |
| Internet | 1 Mbps | 10 Mbps or more |

## 6.4 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11 or later | Backend runtime |
| Node.js | 20 or later | Frontend build tooling |
| Docker | 20 or later | Containerization |
| Git | 2.30 or later | Version control |
| VS Code or Windsurf | Latest | IDE for development |
| Chrome or Firefox | Latest | Browser testing |

## 6.5 Third-Party Services

| Service | Purpose | Cost |
|---------|---------|------|
| Supabase | PostgreSQL database and Authentication | Free tier |
| Render | Docker hosting and Redis cache | Free tier |
| GoDaddy | Domain name (2goi.in) | Approximately 8 dollars per year |
| Resend | Transactional emails | Free tier (3000 per month) |
| Google Cloud Console | OAuth (Login with Google) | Free |
| Google Search Console | SEO indexing | Free |
| UptimeRobot | Uptime monitoring — pings /api/health every 5 min to prevent Render cold starts | Free (50 monitors) |


# 7. System Architecture and Design

## 7.1 Architecture Overview

2GOI uses a single-domain architecture where everything — the frontend, the API, and the redirect service — runs on one domain (2goi.in) in a single Docker container. This simplifies deployment, eliminates CORS (Cross-Origin Resource Sharing) issues, and reduces infrastructure costs.

Here is how the architecture looks at a high level:

```
                         User's Browser
                              |
                              | HTTPS Request
                              v
                    +-------------------+
                    |    2goi.in        |
                    |   Render Cloud    |
                    |   (Docker)        |
                    +-------------------+
                              |
                    +-------------------+
                    |     Gunicorn      |
                    |   (4 workers)     |
                    +-------------------+
                              |
                    +-------------------+
                    |     FastAPI       |
                    |   Application     |
                    +-------------------+
                     /    |     |     \
                    /     |     |      \
                   v      v     v       v
              /api/*   /assets  /{code}  /*
                |        |        |       |
           API Routes  Static   Redirect  SPA
           (JSON)     Files    (302)    Fallback
                |        |        |     (index.html)
                v        v        v
          +--------+  +------+  +-------+
          |Supabase|  | Vite |  | Redis |
          |  DB    |  |Build |  | Cache |
          +--------+  +------+  +-------+

  External Monitoring:
      UptimeRobot --> pings GET /api/health every 5 min
                     (prevents Render free tier from sleeping)
```

The browser sends all requests to a single domain: 2goi.in. The Gunicorn process manager distributes these requests across 4 Uvicorn worker processes. Each worker runs the FastAPI application. FastAPI examines the URL pattern and routes the request to the appropriate handler.

## 7.2 Why Single-Domain Architecture?

In many projects, the frontend and backend are deployed separately. For example, a common setup is to have the frontend at `app.example.com` and the backend at `api.example.com`. This creates several complications:

First, CORS (Cross-Origin Resource Sharing) configuration is required. Browsers restrict requests from one domain to another for security. When your frontend at `app.example.com` tries to call `api.example.com`, the browser blocks the request unless the backend explicitly allows it with CORS headers. This is a common source of bugs and confusion.

Second, separate deployments mean more infrastructure to manage. Two domains, two SSL certificates, two deployment pipelines, and two sets of monitoring.

Third, short URLs would need to be on a separate domain. If your API is at `api.example.com`, your short URLs would be at `api.example.com/2Bi` instead of just `example.com/2Bi`, which defeats the purpose of having short URLs.

Our single-domain approach eliminates all of these problems:

| Benefit | Explanation |
|---------|-------------|
| No CORS needed | Frontend and API are on the same origin (same-origin policy allows all requests) |
| One Docker container | Simpler deployment, lower cost, easier monitoring |
| One SSL certificate | Automatic via Render |
| Short URLs work naturally | 2goi.in/2Bi goes to the same server that serves the frontend and API |
| Fewer moving parts | One service to deploy, monitor, and maintain |

## 7.3 How Requests Are Routed

When a request arrives at 2goi.in, FastAPI routes it based on the URL pattern. The routing follows a priority order:

**Priority 1: API routes (/api/*)** — These are the REST API endpoints. For example, POST /api/shorten creates a new short link, GET /api/links returns the user's links, and GET /api/analytics/2Bi returns click analytics. These routes return JSON responses.

**Priority 2: SEO files (/robots.txt, /sitemap.xml)** — These are static files served directly for search engine crawlers. Google's crawler requests these files to understand what pages to index and what to skip.

**Priority 3: Static assets (/assets/*)** — These are the compiled JavaScript, CSS, and image files that make up the React frontend. Vite generates these files during the build process, and FastAPI serves them as static files.

**Priority 4: URL redirects (/{short_code})** — This is the core feature. When someone visits 2goi.in/2Bi, the redirect router checks if "2Bi" is a valid short code. If it is, the user is redirected (HTTP 302) to the original URL.

**Priority 5: SPA fallback (everything else)** — Any URL that does not match the above patterns is assumed to be a frontend route (like /login, /dashboard, or /analytics/2Bi). FastAPI serves the index.html file, and React Router handles the client-side routing.

This priority order is important. For example, if a user visits 2goi.in/login, we need to serve the React app (not try to redirect as if "login" were a short code). The redirect router checks the database for the short code, and if it does not exist, the request falls through to the SPA fallback.

## 7.4 System Components

### Component 1: FastAPI Application Server

This is the heart of the system. It is a Python web application built with the FastAPI framework. It handles all incoming HTTP requests, executes business logic, and returns responses.

**Responsibilities:**
- Accept and validate API requests using Pydantic schemas
- Generate short codes using Base62 encoding
- Redirect short URLs to their original destinations
- Serve the React frontend as static files
- Authenticate users by verifying JWT tokens
- Apply rate limiting to prevent abuse

**Technology details:** FastAPI runs on Gunicorn (a process manager) with 4 Uvicorn workers. Gunicorn manages the worker processes (restarting them if they crash, distributing requests among them). Uvicorn is an ASGI server that handles the async nature of FastAPI. Together, they can handle many concurrent requests efficiently.

### Component 2: PostgreSQL Database (Supabase)

This is the persistent data store. Everything that needs to survive a server restart is stored here: links, clicks, users, and analytics.

**Responsibilities:**
- Store link mappings (short code to original URL)
- Store click events (who clicked, when, from where)
- Store user accounts
- Maintain sequential IDs for Base62 encoding (PostgreSQL SEQUENCE)
- Enforce data integrity through unique constraints and foreign keys

**Technology details:** We use Supabase's managed PostgreSQL instance, hosted in AWS ap-south-1 (Mumbai). We connect through Supabase's Session Pooler, which provides an IPv4 connection to the IPv6-only database. The connection uses SSL encryption for security.

### Component 3: Redis Cache (Render)

This is the high-speed cache layer. It stores frequently accessed URL mappings so that redirect requests do not need to query the database every time.

**Responsibilities:**
- Cache short code to original URL mappings
- Serve cached URLs in less than 5 milliseconds
- Automatically evict expired links using TTL (Time To Live)
- Fall back gracefully when unavailable (all operations wrapped in try/except)

**Technology details:** Redis is an in-memory key-value store. It keeps all data in RAM, which is why it is so fast compared to disk-based databases like PostgreSQL. The trade-off is that data in Redis is ephemeral — if Redis restarts, the cache is empty. This is acceptable because the cache is merely a performance optimization; the source of truth is always PostgreSQL.

### Component 4: Supabase Auth

This is the authentication service. Instead of implementing our own user registration, password hashing, email verification, and OAuth flows, we use Supabase Auth, which handles all of this out of the box.

**Responsibilities:**
- Email/password registration and login
- Google OAuth integration (Login with Google)
- JWT token issuance and management
- Email confirmation via custom SMTP (Resend)
- Session management and automatic token refresh

**Technology details:** Supabase Auth is built on GoTrue, an open-source authentication service. It issues JWT tokens signed with ES256 (Elliptic Curve Digital Signature Algorithm). Our backend verifies these tokens using Supabase's JWKS (JSON Web Key Set) endpoint, which publishes the public keys needed for verification.

### Component 5: React Frontend

This is the user interface — the visual part of the application that users interact with in their browser.

**Responsibilities:**
- URL shortening form with real-time feedback
- User dashboard showing all created links in a table
- Analytics page with interactive charts (line chart for daily trends, bar chart for countries, pie chart for devices)
- Login and signup pages with email and Google options
- Copy-to-clipboard functionality and QR code display
- Mobile-responsive design that works on all screen sizes

**Technology details:** Built with React 19 (component-based UI library), Vite (fast build tool), TailwindCSS (utility-first CSS framework), Recharts (chart library), and Lucide React (icon library). The frontend is compiled to static HTML, CSS, and JavaScript files during the Docker build process and served by FastAPI.

## 7.5 Component Interaction Diagram

```
+-------------+        +-------------+        +-------------+
|             |  HTTP   |             | SQL    |             |
|   Browser   |-------->|   FastAPI   |------->| PostgreSQL  |
|   (React)   |<--------|   Server    |<-------| (Supabase)  |
|             |  JSON   |             |        |             |
+-------------+        +-------------+        +-------------+
       |                      |
       |                      | Redis Protocol
       |                      v
       |               +-------------+
       |               |   Redis     |
       |               |   Cache     |
       |               +-------------+
       |
       | OAuth/Auth
       v
+-------------+        +-------------+
|  Supabase   |  SMTP   |   Resend    |
|  Auth       |-------->|   (Email)   |
+-------------+        +-------------+
```

The browser communicates with FastAPI over HTTPS. FastAPI talks to PostgreSQL for data persistence and Redis for caching. The browser also communicates directly with Supabase Auth for authentication (login, signup, OAuth). Supabase Auth sends emails through Resend's SMTP service.

## 7.6 Layered Architecture

The backend code follows a clean layered architecture where each layer has a specific responsibility:

**Layer 1: Routers (API Endpoints)**

Routers receive HTTP requests, extract parameters, call service functions, and return HTTP responses. They handle the "web" part of the application — HTTP status codes, headers, request parsing. Routers should contain minimal logic; their job is to bridge HTTP and business logic.

Example: The shorten router receives a POST request, extracts the URL from the body, calls the shortener service, and returns a 201 response with the short URL.

**Layer 2: Services (Business Logic)**

Services contain the core business logic of the application. They implement operations like "create a short link" or "get analytics for a link." Services interact with the database and cache but have no knowledge of HTTP. This separation makes services testable without running a web server.

Example: The shortener service inserts a new link into the database, generates a Base62 code from the sequence ID, caches the URL in Redis, and generates a QR code.

**Layer 3: Models (Database Tables)**

Models define the structure of database tables using SQLAlchemy ORM. They specify column types, constraints, relationships, and indexes. Models contain no logic — they are purely data definitions.

Example: The Link model defines the links table with columns for id, sequence_id, original_url, short_code, user_id, click_count, is_active, created_at, and expires_at.

**Layer 4: Schemas (Request/Response Validation)**

Schemas define the shape of data coming in (requests) and going out (responses) using Pydantic. They validate input data (rejecting invalid URLs, enforcing field lengths) and control what fields appear in API responses.

Example: The LinkCreate schema validates that the URL is a valid HTTP/HTTPS URL, the custom alias (if provided) is 3-20 alphanumeric characters, and expires_in (if provided) is a positive number.

**Why layered architecture matters:**

Separation of concerns means each layer has exactly one job. If we need to change how short codes are generated, we only modify the service layer. If we need to add a new API endpoint, we only add a new router. If we need to add a database column, we only modify the model. Changes in one layer do not require changes in other layers.


# 8. Database Design

## 8.1 Entity-Relationship Diagram

```
+----------+          +----------+          +----------+
|          |  1    N  |          |  1    N  |          |
|  USERS   |--------->|  LINKS   |--------->|  CLICKS  |
|          |          |          |          |          |
+----------+          +----------+          +----------+
                           |
                           | 1    N
                           v
                      +-----------+
                      | DAILY     |
                      | CLICK     |
                      | STATS     |
                      +-----------+
```

**Relationships explained:**

One User can create many Links (one-to-many). This means each link has an optional user_id that references the users table. The relationship is optional because anonymous users can also create links (user_id is NULL).

One Link can have many Clicks (one-to-many). Every time someone clicks a short URL, a new row is inserted into the clicks table with the link_id.

One Link can have many Daily Click Stats (one-to-many). For each day that a link receives clicks, there is one row in the daily_click_stats table. This is the pre-aggregated data used for the daily trend chart.

## 8.2 Table 1: links

This is the core table that stores all shortened URLs.

```sql
CREATE TABLE links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id BIGINT UNIQUE NOT NULL DEFAULT nextval('links_sequence_id_seq'),
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    click_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);
```

**Column-by-column explanation:**

**id (UUID):** The primary key. We use UUIDs (Universally Unique Identifiers) instead of auto-incrementing integers for security. If the primary key were an auto-incrementing integer like 5000, an attacker could guess that approximately 5000 links exist in the system. UUIDs like "a1b2c3d4-e5f6-7890-abcd-ef1234567890" reveal nothing about how many records exist.

**sequence_id (BIGINT):** An auto-incrementing number generated by a PostgreSQL SEQUENCE. This number is used exclusively for Base62 encoding to generate the short code. The sequence starts at 10000 to ensure all codes are at least 3 characters long. This is separate from the UUID primary key because UUIDs are too long for short codes.

**original_url (TEXT):** The destination URL that the short link points to. TEXT type allows URLs of any length (up to 1 GB in PostgreSQL, though in practice URLs rarely exceed a few thousand characters).

**short_code (VARCHAR 20):** The short code that appears in the URL (like "2Bi" or "myresume"). The UNIQUE constraint ensures no two links have the same code. The INDEX on this column ensures fast lookups during redirects.

**user_id (UUID, nullable):** References the users table. NULL means the link was created by an anonymous user. ON DELETE SET NULL means if a user is deleted, their links remain but become unowned.

**click_count (INTEGER):** A denormalized count of total clicks. "Denormalized" means this data is technically redundant (we could always count rows in the clicks table), but storing it here avoids a slow COUNT query every time we display the dashboard. It is updated atomically on every click using `click_count = click_count + 1`.

**is_active (BOOLEAN):** A soft-delete flag. When a user "deletes" a link, we set is_active to FALSE instead of actually removing the row from the database. This preserves click history and allows for potential recovery. The redirect router checks this flag and returns a 404 for inactive links.

**created_at (TIMESTAMPTZ):** When the link was created. TIMESTAMPTZ stores the timestamp with timezone information, which is important for accurate time display across different time zones.

**expires_at (TIMESTAMPTZ, nullable):** When the link should expire. NULL means the link never expires. The redirect router checks this value and returns HTTP 410 (Gone) for expired links. Redis also uses this to set a TTL on the cached entry, so expired links are automatically removed from the cache.

## 8.3 Table 2: clicks

This table stores every click event as a raw record. Each row represents one person clicking one short link at one point in time.

```sql
CREATE TABLE clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    country VARCHAR(10),
    browser VARCHAR(50),
    device_type VARCHAR(20),
    referrer VARCHAR(2048),
    ip_hash VARCHAR(64),
    clicked_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Column-by-column explanation:**

**link_id (UUID):** Which link was clicked. This is a foreign key to the links table. ON DELETE CASCADE means if a link is permanently deleted (not just soft-deleted), all its click records are also deleted.

**country (VARCHAR 10):** The visitor's country code, like "US" for United States or "IN" for India. This is determined from the visitor's IP address using geolocation. In our current implementation, this is parsed from request headers provided by the hosting platform.

**browser (VARCHAR 50):** The browser name, like "Chrome", "Safari", or "Firefox". This is parsed from the User-Agent HTTP header that every browser sends with each request.

**device_type (VARCHAR 20):** Either "mobile", "tablet", or "desktop". Also parsed from the User-Agent header by checking for keywords like "Mobile", "iPad", "Android", etc.

**referrer (VARCHAR 2048):** The URL of the page that the user was on before clicking the short link. For example, if someone clicks a short link in a Twitter post, the referrer would be "https://twitter.com/...". This is from the Referer HTTP header. Note: the referrer can be empty if the user typed the URL directly or if the referrer is stripped for privacy.

**ip_hash (VARCHAR 64):** A SHA-256 hash of the visitor's IP address. We deliberately do not store raw IP addresses for privacy reasons. Privacy laws like GDPR (Europe) and CCPA (California) consider IP addresses as personal data. By hashing the IP, we can still detect unique visitors (the same IP always produces the same hash) without being able to reverse the hash to find the actual IP.

**clicked_at (TIMESTAMPTZ):** When the click happened. Used for time-based analytics queries.

## 8.4 Table 3: daily_click_stats

This table stores pre-aggregated click counts per link per day. It is an optimization that makes analytics queries dramatically faster.

```sql
CREATE TABLE daily_click_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    click_count INTEGER DEFAULT 0,
    UNIQUE(link_id, date)
);
```

**The UNIQUE constraint on (link_id, date) is the most important design decision in this table.** It enables the upsert pattern, which is explained in detail in Section 14 (Click Analytics Engine).

**Why pre-aggregate?**

Without aggregation, getting "clicks per day for the last 30 days" requires scanning ALL click rows for that link:

```sql
-- SLOW: Scans every click row for this link
SELECT DATE(clicked_at) as day, COUNT(*) as clicks
FROM clicks
WHERE link_id = 'some-uuid'
GROUP BY DATE(clicked_at)
ORDER BY day DESC
LIMIT 30;
```

If a link has 1,000,000 clicks, this query scans 1,000,000 rows just to produce 30 numbers. As the clicks table grows, this query gets slower and slower.

With pre-aggregation:

```sql
-- FAST: Only reads 30 rows, regardless of total clicks
SELECT date, click_count
FROM daily_click_stats
WHERE link_id = 'some-uuid'
ORDER BY date DESC
LIMIT 30;
```

This always reads exactly 30 rows. Whether the link has 100 clicks or 100,000,000 clicks, this query takes the same amount of time.

## 8.5 Table 4: users

This table stores user account information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Why maintain a separate users table when Supabase Auth already has user data?**

First, our links table needs a user_id foreign key. Foreign keys must reference a table in the same database. Supabase Auth's internal auth.users table is in a different schema with different access rules. Our own users table in the public schema is easily referenceable.

Second, we can add custom fields that Supabase Auth does not have. The `plan` field (currently always "free") is ready for future premium tiers.

Third, independence from Supabase. If we ever migrate to a different authentication provider, our data remains self-contained.

**Auto-creation:** When a user makes their first authenticated API call, our auth middleware checks if a matching user record exists in our users table. If not, it creates one automatically. This means users never need to "register" in our database — it happens transparently on their first API call.

## 8.6 Indexing Strategy

Indexes are data structures that speed up database queries at the cost of slower writes and additional storage. Choosing the right indexes is critical for performance.

| Index | Table | Column(s) | Purpose |
|-------|-------|-----------|---------|
| Primary key | links | id | Every primary key is automatically indexed |
| Unique | links | sequence_id | Fast lookup by sequence ID, ensures uniqueness |
| Unique | links | short_code | Fast redirect lookup (the most critical index) |
| Regular | links | user_id | Fast filtering of links by user (dashboard page) |
| Primary key | clicks | id | Automatic |
| Regular | clicks | link_id | Fast analytics queries (filter clicks by link) |
| Regular | clicks | clicked_at | Time-range queries |
| Composite | clicks | (link_id, clicked_at) | Combined filter for analytics within a date range |
| Primary key | daily_click_stats | id | Automatic |
| Unique composite | daily_click_stats | (link_id, date) | Upsert pattern and fast lookup |

The most critical index is the unique index on `links.short_code`. This index is used for every single redirect request. Without it, every redirect would require a full table scan.

## 8.7 Data Flow Through Tables

Here is how data flows through the database when a link is created and then clicked:

**Step 1: User shortens a URL**

The user submits "https://www.google.com" in the shortening form.

```
INSERT INTO links (original_url, short_code) VALUES ('https://www.google.com', '__pending__')
→ PostgreSQL generates sequence_id = 10008
→ Backend reads sequence_id, encodes to Base62: 10008 → "2Bq"
→ UPDATE links SET short_code = '2Bq' WHERE sequence_id = 10008
→ Redis: SET "url:2Bq" "https://www.google.com"
→ Return short URL: https://2goi.in/2Bq
```

**Step 2: Someone clicks the short link**

A visitor opens https://2goi.in/2Bq in their browser.

```
→ Redis: GET "url:2Bq" → "https://www.google.com" (cache hit, 3ms)
→ HTTP 302 Redirect to https://www.google.com
→ Background task (does not block the redirect):
  → Parse User-Agent: browser="Chrome", device="desktop"
  → Hash IP: SHA256("203.0.113.42") = "a1b2c3d4..."
  → INSERT INTO clicks (link_id, country, browser, device_type, ip_hash) VALUES (...)
  → UPSERT INTO daily_click_stats: INSERT ... ON CONFLICT ... SET click_count + 1
  → UPDATE links SET click_count = click_count + 1 WHERE id = ...
```

**Step 3: User views analytics**

The link owner visits the analytics page.

```
→ SELECT click_count FROM links WHERE short_code = '2Bq' → 42 total clicks
→ SELECT country, COUNT(*) FROM clicks WHERE link_id = ... GROUP BY country → country breakdown
→ SELECT device_type, COUNT(*) FROM clicks WHERE link_id = ... GROUP BY device_type → device breakdown
→ SELECT browser, COUNT(*) FROM clicks WHERE link_id = ... GROUP BY browser → browser breakdown
→ SELECT date, click_count FROM daily_click_stats WHERE link_id = ... ORDER BY date → daily trend
```


# 9. Detailed Module Descriptions

## 9.1 Module Overview

The backend is organized into clear modules, each with a specific responsibility:

```
backend/app/
├── main.py              → Application entry point, routing, SPA serving
├── config.py            → Configuration from environment variables
├── database.py          → Async database engine and session management
├── redis_client.py      → Redis connection for caching
├── auth.py              → JWT verification and user management
├── middleware.py         → Rate limiting
├── models/              → Database table definitions (4 files)
├── schemas/             → Request/response validation (3 files)
├── services/            → Business logic (2 files)
└── routers/             → API endpoint handlers (5 files)
```

## 9.2 Module: Configuration (config.py)

**Purpose:** Load all application settings from environment variables into a typed Python object.

This module uses Pydantic's BaseSettings class, which automatically reads values from environment variables and from a .env file. Every setting has a type annotation, and Pydantic validates the values at startup. If a required setting is missing or has the wrong type, the application fails immediately with a clear error message. This is called "fail fast" and is a best practice because it prevents the application from running with invalid configuration.

Settings include:
- Database connection strings (async and sync versions)
- Supabase credentials (URL, service role key, anon key, JWT secret)
- Redis connection URL
- Base URL for constructing short links
- Rate limiting thresholds
- CORS origins
- Environment mode (development or production)

## 9.3 Module: Database (database.py)

**Purpose:** Set up the async SQLAlchemy engine and provide database sessions to route handlers.

This module creates an async database engine with connection pooling. Connection pooling is a critical optimization. Opening a new database connection takes approximately 50 to 100 milliseconds because it involves a TCP handshake, SSL negotiation, and authentication. If we opened a new connection for every request, this overhead would add up quickly.

With connection pooling, we keep a pool of pre-established connections. When a request needs a database connection, it borrows one from the pool (instant). When it is done, it returns the connection to the pool. The pool is configured with:

- **pool_size = 5**: Keep 5 connections always ready
- **max_overflow = 10**: Allow up to 15 total connections (5 + 10) during traffic spikes
- **pool_recycle = 3600**: Close and reopen connections after 1 hour to prevent stale connections

The module also configures SSL for the database connection, which is required by Supabase.

## 9.4 Module: Redis Client (redis_client.py)

**Purpose:** Manage the Redis connection for caching URL lookups.

This module creates an async Redis client and provides a function to get the Redis connection. The key design decision is that Redis is optional. If Redis is unavailable (network issue, service down, etc.), the function returns None, and all Redis operations throughout the application gracefully skip caching and fall back to database queries.

This is implemented by wrapping every Redis operation in try/except blocks:

```python
async def get_cached_url(short_code):
    try:
        redis = await get_redis()
        if redis:
            cached = await redis.get(f"url:{short_code}")
            if cached:
                return cached.decode()
    except Exception:
        pass  # Redis failed, that is okay
    return None
```

## 9.5 Module: Authentication (auth.py)

**Purpose:** Verify JWT tokens from Supabase and manage user records in our database.

This is one of the most complex modules. It handles three things:

**ES256 JWT verification using JWKS:** When a user makes an authenticated API call, their request includes a JWT token in the Authorization header. The backend needs to verify that this token was actually issued by Supabase (not forged by an attacker). It does this by fetching Supabase's public keys from the JWKS endpoint and using them to verify the token's digital signature.

**HS256 fallback:** As a fallback, the module can also verify tokens using HS256 (a symmetric algorithm using a shared secret). This provides compatibility with different token types.

**Auto-creation of user records:** When the token is verified, the module extracts the user_id from the token's "sub" claim. It then checks if a matching user exists in our users table. If not, it creates one automatically. This means users never need to explicitly "register" in our database.

## 9.6 Module: Rate Limiting (middleware.py)

**Purpose:** Prevent abuse by limiting the number of requests a user can make per minute.

Without rate limiting, a malicious user could:
- Create millions of short links, consuming database storage
- Send millions of redirect requests, overloading the server
- Make rapid API calls, degrading performance for other users

The rate limiter uses the SlowAPI library, which tracks request counts per IP address. Anonymous users are limited to 100 requests per minute. Authenticated users get 1000 requests per minute. When a user exceeds their limit, the API returns HTTP 429 (Too Many Requests).

## 9.7 Module: Services (services/)

### shortener.py — URL Shortening Service

This service contains the core business logic for URL shortening:

**encode_base62(num):** Converts a positive integer to a Base62 string. This is the pure mathematical function that turns sequence IDs into short codes.

**create_short_link(db, url, user_id, custom_alias, expires_in):** Creates a new short link. For regular links, it inserts a record with a temporary short_code, reads the generated sequence_id, encodes it to Base62, and updates the record. For custom aliases, it checks if the alias is already taken and uses it directly.

**get_original_url(db, short_code):** Looks up a short code, first checking Redis cache, then falling back to a database query. Returns the original URL or None.

**generate_qr_code(url):** Creates a QR code image for a given URL. The QR code is generated as a PNG image, encoded to Base64, and returned as a string that can be embedded in an HTML img tag or returned in an API response.

### analytics.py — Analytics Service

This service handles click tracking and analytics:

**log_click(db, link_id, request):** Called as a background task after every redirect. It parses the User-Agent header to determine the browser and device type, hashes the IP address, and inserts a new row into the clicks table. It also performs the daily_click_stats upsert and increments the link's click_count.

**get_analytics(db, short_code, days):** Retrieves comprehensive analytics for a link. It runs multiple queries in parallel: total clicks, country breakdown, device breakdown, browser breakdown, and daily click trend. The results are assembled into a structured response.

## 9.8 Module: Routers (routers/)

### shorten.py — POST /api/shorten

Handles link creation. Receives the URL (and optional custom alias and expiration), calls the shortener service, and returns the short URL with QR code. Authentication is optional — both anonymous and authenticated users can shorten URLs.

### redirect.py — GET /{short_code}

Handles redirects. This is the most performance-critical endpoint because it is called on every short link click. It checks Redis first (cache hit path is less than 5ms), falls back to PostgreSQL (cache miss path is 20-50ms), and returns an HTTP 302 redirect. Click logging runs as a background task so it does not block the redirect response.

### links.py — GET /api/links and DELETE /api/links/{id}

Handles link management. GET returns a paginated list of the authenticated user's links, sorted by creation date, click count, or expiration date. DELETE performs a soft-delete (sets is_active to false) and removes the URL from Redis cache.

### analytics.py — GET /api/analytics/{short_code}

Handles analytics retrieval. Verifies that the authenticated user owns the link, then retrieves and returns all analytics data (total clicks, country/device/browser breakdowns, daily trend).

### health.py — GET/HEAD /api/health

Handles health checks. Tests connectivity to both PostgreSQL and Redis, and returns the status of each. Accepts both GET and HEAD HTTP methods for compatibility with monitoring tools. Render uses this endpoint to monitor application health, and UptimeRobot pings this endpoint every 5 minutes to prevent the Render free tier container from sleeping (cold start prevention).
# 10. API Design

## 10.1 RESTful API Principles

Our API follows REST (Representational State Transfer) principles, which is the standard approach for building web APIs:

**Resources are nouns, not verbs.** We use `/api/links` instead of `/api/getLinks`. The HTTP method (GET, POST, DELETE) is the verb.

**HTTP methods have specific meanings.** GET retrieves data, POST creates data, DELETE removes data. This makes the API predictable and self-documenting.

**Stateless requests.** Each request contains all the information the server needs to process it. Authentication is done via a JWT token in the Authorization header. The server does not store session data between requests.

**JSON responses.** All API endpoints return JSON data. This is the universal format for web APIs, easily consumed by any frontend framework or programming language.

## 10.2 Endpoint Details

### POST /api/shorten — Create a Short Link

This is the endpoint that creates a new short URL. It accepts a JSON body with the original URL and optional parameters.

**Request body example:**
```json
{
    "url": "https://www.example.com/very/long/path?with=parameters",
    "custom_alias": "mylink",
    "expires_in": 86400
}
```

The `url` field is required and must be a valid HTTP or HTTPS URL. Pydantic validates this automatically using the HttpUrl type. If someone submits "not-a-url" or "ftp://something", the API returns a 422 Validation Error.

The `custom_alias` field is optional. If provided, it must be 3 to 20 characters long and contain only alphanumeric characters, hyphens, and underscores. The regex pattern used for validation is `^[a-zA-Z0-9_-]{3,20}$`. If the alias is already taken by another link, the API returns 409 Conflict.

The `expires_in` field is optional. It specifies the number of seconds until the link expires. For example, 86400 seconds is 24 hours. After expiration, the short link returns HTTP 410 (Gone) instead of redirecting.

**Response example (201 Created):**
```json
{
    "short_url": "https://2goi.in/mylink",
    "short_code": "mylink",
    "original_url": "https://www.example.com/very/long/path?with=parameters",
    "qr_code": "iVBORw0KGgoAAAANSUhEUg...",
    "expires_at": "2026-03-18T09:00:00Z"
}
```

The `qr_code` field contains a Base64-encoded PNG image of a QR code. The frontend can display this directly in an img tag using `data:image/png;base64,{qr_code}`.

### GET /{short_code} — Redirect

This is the core endpoint. When someone visits `https://2goi.in/2Bi`, this endpoint looks up the short code "2Bi" and redirects to the original URL.

The response is HTTP 302 (Found) with a Location header pointing to the original URL. The browser automatically follows this redirect and loads the original page. The entire process takes 3 to 5 milliseconds for a cache hit.

Error responses: 404 if the short code does not exist or the link is inactive. 410 (Gone) if the link has expired.

### GET /api/links — List User's Links

Returns a paginated list of links created by the authenticated user. Supports sorting by creation date, click count, or expiration date. Pagination uses page and page_size query parameters.

### DELETE /api/links/{link_id} — Delete a Link

Soft-deletes a link by setting is_active to false. Also removes the URL from Redis cache so that redirect attempts return 404. The user must be the owner of the link.

### GET /api/analytics/{short_code} — Get Analytics

Returns comprehensive click analytics for a specific link. The user must be the owner. The response includes total click count, country breakdown (top countries by clicks), device breakdown (mobile vs desktop vs tablet), browser breakdown (Chrome vs Safari vs Firefox etc.), and daily click trend (clicks per day for the specified number of days).

### GET /api/health — Health Check

Returns the health status of the application and its dependencies (database and Redis). Used by Render for monitoring. Returns "healthy" if both dependencies are connected, "degraded" if Redis is down but the database is fine, and "unhealthy" if the database is down.


# 11. Authentication System

## 11.1 Overview

Authentication is the process of verifying who a user is. In 2GOI, we use Supabase Auth to handle all authentication. This means we do not store passwords, manage sessions, or implement email verification ourselves. Supabase handles all of that. Our backend's only job is to verify the JWT tokens that Supabase issues.

## 11.2 Authentication Methods

### Method 1: Email and Password

The flow for email/password authentication works as follows:

1. The user goes to the signup page at /signup
2. They enter their email address and choose a password (minimum 6 characters)
3. The frontend calls Supabase: `supabase.auth.signUp({ email, password })`
4. Supabase creates the user in its authentication system
5. Supabase sends a confirmation email to the user's email address (via Resend SMTP)
6. The user opens the email and clicks the confirmation link
7. The user's email is now verified and they can log in
8. The user goes to the login page at /login and enters their credentials
9. The frontend calls Supabase: `supabase.auth.signInWithPassword({ email, password })`
10. Supabase verifies the credentials and returns a JWT token
11. The Supabase JavaScript client automatically stores the token in the browser's localStorage
12. On every subsequent API request, our Axios interceptor reads the token from Supabase and attaches it to the request as an Authorization header

### Method 2: Google OAuth

Google OAuth allows users to log in using their existing Google account. The flow is:

1. The user clicks "Continue with Google" on the login or signup page
2. The frontend calls: `supabase.auth.signInWithOAuth({ provider: 'google' })`
3. The browser redirects to Google's login page (accounts.google.com)
4. The user enters their Google credentials or selects their Google account
5. Google asks the user to grant permission (email and profile access)
6. Google redirects back to Supabase's callback URL with an authorization code
7. Supabase exchanges the code for Google's user information
8. Supabase creates or updates the user account
9. Supabase issues a JWT token
10. Supabase redirects the browser to our application at /dashboard with the token

The beauty of this flow is that we never see the user's Google password. Google handles the password verification, and we only receive a token that confirms the user's identity.

## 11.3 JWT Tokens Explained

JWT stands for JSON Web Token. It is an open standard (RFC 7519) for securely transmitting information between parties. A JWT consists of three parts separated by dots:

```
eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiIxMjM0IiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIn0.signature
```

**Part 1: Header** — Contains the algorithm used to sign the token (ES256 in our case) and the token type (JWT).

**Part 2: Payload** — Contains claims (statements about the user). The most important claim for us is "sub" (subject), which contains the user's UUID. Other claims include email, expiration time, and issued-at time.

**Part 3: Signature** — A cryptographic signature that proves the token was issued by Supabase and has not been tampered with. If anyone modifies the payload (for example, changing the user ID), the signature becomes invalid.

## 11.4 Token Verification on the Backend

When the backend receives a request with a JWT token, it needs to verify three things:

1. **Is the signature valid?** This proves the token was issued by Supabase and has not been modified.
2. **Has the token expired?** The "exp" claim contains the expiration time. If the current time is past this, the token is rejected.
3. **Is the token for our application?** The "aud" (audience) claim should be "authenticated".

We verify tokens using Supabase's JWKS (JSON Web Key Set) endpoint. JWKS is a protocol where the authentication provider publishes its public keys at a well-known URL. Our backend fetches these keys and uses them to verify the token's signature.

This approach has a major advantage: key rotation. If Supabase needs to change its signing keys (for security), it simply publishes new keys at the JWKS endpoint. Our backend automatically fetches the new keys on the next verification. No code changes or redeployment required.

## 11.5 Frontend Token Management

The Supabase JavaScript client handles all token management automatically. Tokens are stored in the browser's localStorage. When a token is about to expire (they expire after 1 hour), the client uses a refresh token to obtain a new access token. This happens transparently — the user does not notice.

Our Axios HTTP client has an interceptor that attaches the current token to every API request:

```javascript
api.interceptors.request.use(async (config) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session) {
        config.headers.Authorization = `Bearer ${session.access_token}`
    }
    return config
})
```

This means every API call automatically includes the user's authentication, and the backend can identify who is making the request.

## 11.6 Protected Routes on the Frontend

Some pages in the React application require the user to be logged in. These are called protected routes. We implement this with a ProtectedRoute component:

When a user tries to access /dashboard or /analytics without being logged in, the ProtectedRoute component detects that there is no authenticated user and redirects them to /login. After logging in, they are taken to the originally requested page.


# 12. URL Shortening Algorithm (Base62)

## 12.1 What is Base62 Encoding?

Base62 is a number encoding system that uses 62 characters to represent numbers. It is similar to how we normally count using Base10 (decimal, using digits 0 through 9), but instead of 10 symbols, it uses 62 symbols.

The 62 characters are: 0 through 9 (ten digits), a through z (26 lowercase letters), and A through Z (26 uppercase letters).

This means each "digit" in a Base62 number can represent 62 different values, compared to 10 values for a decimal digit. This is why Base62 numbers are much shorter than decimal numbers for the same value.

## 12.2 The Encoding Algorithm

The algorithm is simple division with remainder, similar to how you convert decimal to binary:

```python
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num):
    if num == 0:
        return CHARSET[0]
    
    result = []
    while num > 0:
        remainder = num % 62
        result.append(CHARSET[remainder])
        num = num // 62
    
    return ''.join(reversed(result))
```

**Detailed example: Encoding the number 10000**

```
Step 1: 10000 divided by 62 = 161, remainder = 18
        CHARSET[18] = 'i'
        
Step 2: 161 divided by 62 = 2, remainder = 37
        CHARSET[37] = 'B'
        
Step 3: 2 divided by 62 = 0, remainder = 2
        CHARSET[2] = '2'
        
Collect remainders in reverse order: "2Bi"
```

So the number 10000 becomes the short code "2Bi". The URL would be https://2goi.in/2Bi.

## 12.3 Capacity Analysis

The number of unique codes depends on the code length:

| Code Length | Unique Codes | Range |
|-------------|-------------|-------|
| 1 character | 62 | 0 to 61 |
| 2 characters | 3,844 | 62 to 3,843 |
| 3 characters | 238,328 | 3,844 to 238,327 |
| 4 characters | 14,776,336 | 238,328 to 14,776,335 |
| 5 characters | 916,132,832 | 14,776,336 to 916,132,831 |
| 6 characters | 56,800,235,584 | 916,132,832 to 56,800,235,583 |
| 7 characters | 3,521,614,606,208 | More than 3.5 trillion |

With just 6 characters, we can support over 56 billion unique short codes. That is more than enough for any practical application. Even if we created 1 million new links every day, it would take over 155,000 years to exhaust 6-character codes.

## 12.4 Why Start the Sequence at 10000?

Our PostgreSQL sequence starts at 10000 instead of 0 or 1. This is because:

Numbers 0 through 61 produce 1-character codes (like "0", "a", "Z"). These are too short and could conflict with URL routes or look unprofessional.

Numbers 62 through 3843 produce 2-character codes (like "10", "ab"). These are still quite short and limited in number.

By starting at 10000, all codes are guaranteed to be at least 3 characters (10000 in Base62 is "2Bi"). Three-character codes look professional, are easy to type, and give us 228,328 codes in the 3-character range alone.

## 12.5 Why Base62 Instead of Base64?

Base64 is more common in computing (used for encoding binary data). It uses the same 62 characters as Base62 plus two additional characters: + and /. We chose Base62 because the + and / characters have special meanings in URLs. The + character is interpreted as a space in some contexts, and the / character separates URL path segments. By using only URL-safe characters (alphanumeric), our short codes work correctly when embedded in any URL, email, or message without encoding issues.

## 12.6 The Complete Link Creation Process

Here is the complete process that happens when a user shortens a URL:

1. The user submits a URL through the frontend form
2. The frontend sends a POST request to /api/shorten with the URL
3. The shorten router validates the URL using Pydantic's HttpUrl type
4. If a custom alias is provided, the service checks if it already exists in the database
5. For standard (non-custom) links: a new row is inserted into the links table with short_code set to a temporary placeholder value
6. PostgreSQL automatically generates a unique sequence_id for the new row
7. The service reads the sequence_id and passes it to the encode_base62 function
8. The Base62 code is computed and the links row is updated with the actual short_code
9. The URL is cached in Redis with the key pattern "url:{short_code}"
10. If the link has an expiration time, the Redis entry is set with a matching TTL
11. A QR code is generated as a PNG image and encoded to Base64
12. The response is returned to the frontend with the short URL, QR code, and other details


# 13. Caching Strategy (Redis)

## 13.1 Why Use a Cache?

The redirect endpoint (GET /{short_code}) is the most frequently called endpoint in the entire application. Every time someone clicks a short link, the system needs to look up the original URL. Without caching, every redirect requires a database query.

Database queries are relatively slow because they involve network communication, query parsing, disk I/O (if the data is not in PostgreSQL's buffer cache), and result serialization. A typical PostgreSQL query takes 20 to 50 milliseconds.

Redis, on the other hand, stores all data in RAM (memory). Reading from memory is orders of magnitude faster than reading from disk. A typical Redis read takes 1 to 5 milliseconds.

For a popular link that receives 100,000 clicks per day, the difference is significant. Without Redis, the database handles 100,000 queries for just one link. With Redis, only the first click (cache miss) requires a database query. The remaining 99,999 clicks are served from the cache.

## 13.2 The Cache-Aside Pattern

We use the cache-aside (also called lazy loading) pattern. In this pattern, the application first checks the cache. If the data is found (cache hit), it is returned immediately. If not found (cache miss), the application queries the database, stores the result in the cache, and then returns it.

```
Request: GET /2Bq
    |
    v
Check Redis: GET "url:2Bq"
    |
    +--> Cache HIT: Return cached URL (3-5ms total)
    |
    +--> Cache MISS:
            |
            v
         Query PostgreSQL: SELECT original_url FROM links WHERE short_code = '2Bq'
            |
            v
         Store in Redis: SET "url:2Bq" "https://original-url.com"
            |
            v
         Return URL (20-50ms total, but next request will be a cache hit)
```

In practice, we also proactively cache URLs when links are created. This means the very first click on a new link will usually be a cache hit, providing the best possible user experience.

## 13.3 Redis Key Design

All cached URLs use a simple key pattern: "url:" followed by the short code.

```
Key:    "url:2Bq"
Value:  "https://www.google.com/search?q=hello"
```

The "url:" prefix acts as a namespace. This is important because Redis is a general-purpose key-value store that might be used for other purposes in the future (like session storage or rate limiting). The prefix ensures URL cache keys do not collide with keys used for other purposes.

## 13.4 Cache Expiry for Expiring Links

When a link has an expiration time, we set a matching TTL (Time To Live) on the Redis key:

```python
# Link expires in 24 hours (86400 seconds)
await redis.setex(f"url:{short_code}", 86400, original_url)
```

Redis automatically deletes the key after the TTL expires. This has two benefits. First, expired links stop being served from the cache without any manual cleanup. Second, memory is automatically freed when expired keys are deleted.

For links without expiration, no TTL is set, and the key remains in Redis until it is explicitly deleted or evicted due to memory pressure.

## 13.5 What Happens When Redis Fails

Redis is designed to be optional. Every Redis operation in the application is wrapped in a try-except block. If Redis is unavailable for any reason (network issue, service restart, out of memory), the application gracefully falls back to database queries.

This means:
- Redirects still work (slightly slower, 20-50ms instead of 3-5ms)
- Link creation still works (the cache priming step is skipped)
- Analytics still work (they do not depend on Redis)
- The health endpoint reports Redis as "disconnected" but the overall status is "degraded" not "unhealthy"

This design choice prioritizes availability over performance. It is better to serve a request slowly than to not serve it at all.

## 13.6 Memory Management

Render's free Redis tier provides 25 MB of memory. With an average URL length of 100 characters and a key overhead of about 50 bytes, each cached entry uses approximately 150 bytes. This means we can cache about 170,000 URLs in 25 MB.

If memory runs out, Redis uses the allkeys-lru eviction policy (configured in render.yaml). LRU stands for Least Recently Used. When Redis needs to free memory, it removes the keys that have not been accessed for the longest time. This is the ideal policy for a URL cache because popular links (frequently clicked) stay in the cache while rarely-clicked links are evicted.


# 14. Click Analytics Engine

## 14.1 Overview

Every time someone clicks a short link, the system records metadata about the click. This data powers the analytics dashboard, which shows link owners:
- Total number of clicks
- Which countries clicks came from
- What devices were used (mobile, desktop, tablet)
- What browsers were used (Chrome, Safari, Firefox, etc.)
- Daily click trends over time

## 14.2 Asynchronous Click Logging

The most important design decision in the analytics engine is that click logging is asynchronous. When someone clicks a short link, the redirect happens immediately. The click logging happens in the background, after the redirect response has been sent.

```
Request: GET /2Bq
    |
    v
Look up original URL (Redis or DB)
    |
    v
Send HTTP 302 Redirect to user    <-- User gets redirected here (3-5ms)
    |
    v
Background Task: Log the click     <-- This happens AFTER the response is sent
    - Parse User-Agent header
    - Hash IP address
    - Insert into clicks table
    - Upsert daily_click_stats
    - Increment link click_count
```

FastAPI's BackgroundTasks feature makes this possible. The redirect handler adds a background task and returns the response immediately. The background task runs after the response is sent, so it does not add any latency to the redirect.

This is critical for user experience. If click logging were synchronous, every redirect would take an additional 20-50ms (for the database inserts). Over millions of redirects, this would significantly degrade performance.

## 14.3 Parsing Click Metadata

### Browser and Device Detection

Every HTTP request includes a User-Agent header that identifies the browser and device. For example:

```
Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1
```

We parse this header to extract:
- **Browser:** "Safari" (from "Safari/604.1")
- **Device type:** "mobile" (from "Mobile" keyword and "iPhone")

The parsing logic checks for keywords:
- Contains "Mobile" or "Android" or "iPhone" → mobile
- Contains "iPad" or "Tablet" → tablet
- Otherwise → desktop

For browsers, we check for "Chrome", "Safari", "Firefox", "Edge", "Opera", and "Samsung" in the User-Agent string. The order matters because Chrome's User-Agent contains "Safari" (Chrome is based on WebKit), so we check for "Chrome" first.

### IP Address Privacy

We record the visitor's IP address for analytics, but we never store the raw IP. Instead, we hash it using SHA-256:

```python
import hashlib
ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
```

This one-way hash means:
- The same IP always produces the same hash (so we can count unique visitors)
- The hash cannot be reversed to find the original IP
- We comply with privacy regulations like GDPR and CCPA

## 14.4 The Daily Upsert Pattern

The most elegant piece of the analytics engine is the daily click stats upsert. On every click, we execute this SQL statement:

```sql
INSERT INTO daily_click_stats (link_id, date, click_count)
VALUES ('some-uuid', '2026-03-17', 1)
ON CONFLICT (link_id, date)
DO UPDATE SET click_count = daily_click_stats.click_count + 1;
```

This single statement handles two cases:

**First click of the day:** If there is no row for this link on this date, PostgreSQL inserts a new row with click_count = 1.

**Every subsequent click that day:** If a row already exists for this link on this date, the UNIQUE constraint on (link_id, date) causes a conflict. The ON CONFLICT clause tells PostgreSQL to update the existing row by incrementing click_count by 1.

This is called an "upsert" (a portmanteau of UPDATE and INSERT) and it is an atomic operation. Even if 100 clicks arrive simultaneously for the same link, PostgreSQL handles the concurrency correctly. No race conditions, no lost updates.

## 14.5 Analytics Queries

When a user views the analytics page, the backend runs several queries:

**Total clicks:** Read directly from the links table's click_count column. This is a single row lookup, not a COUNT aggregation.

**Country breakdown:**
```sql
SELECT country, COUNT(*) as count
FROM clicks
WHERE link_id = :link_id AND clicked_at >= :start_date
GROUP BY country
ORDER BY count DESC
```

**Device breakdown:**
```sql
SELECT device_type, COUNT(*) as count
FROM clicks
WHERE link_id = :link_id AND clicked_at >= :start_date
GROUP BY device_type
ORDER BY count DESC
```

**Browser breakdown:**
```sql
SELECT browser, COUNT(*) as count
FROM clicks
WHERE link_id = :link_id AND clicked_at >= :start_date
GROUP BY browser
ORDER BY count DESC
```

**Daily trend (from pre-aggregated table):**
```sql
SELECT date, click_count
FROM daily_click_stats
WHERE link_id = :link_id AND date >= :start_date
ORDER BY date ASC
```

The daily trend query is the fastest because it reads from the pre-aggregated table. Instead of scanning potentially millions of raw click rows, it reads at most 365 rows (one per day for a year).


# 15. Frontend Design

## 15.1 Technology Choices

The frontend is built with the following technologies:

**React 19:** A JavaScript library for building user interfaces using a component-based architecture. Each part of the UI (navbar, form, chart) is a self-contained component that manages its own state and rendering.

**Vite:** A modern build tool that is significantly faster than alternatives like Webpack. During development, Vite provides instant hot module replacement (changes appear in the browser immediately without a full page reload). For production, Vite bundles all code into optimized JavaScript and CSS files.

**TailwindCSS:** A utility-first CSS framework. Instead of writing CSS in separate files, you apply small utility classes directly in the HTML. For example, `className="bg-slate-900 text-white p-4 rounded-xl"` creates a dark background, white text, padding, and rounded corners. This approach is faster to develop with and produces smaller CSS bundles because unused styles are automatically removed.

**Recharts:** A chart library built specifically for React. We use it for the analytics page to display line charts (daily trend), bar charts (countries), and pie charts (devices).

**Lucide React:** An icon library that provides clean, consistent SVG icons. We use icons throughout the UI for visual clarity.

## 15.2 Page Descriptions

### Home Page (/)

The landing page is the first thing users see. It contains:

**Hero section:** A large heading that says "Shorten Your URLs with Confidence" with a gradient text effect. Below is a brief description of the service.

**URL shortening form:** The main feature. Users paste a long URL, optionally set a custom alias and expiration time, and click "Shorten URL". The result appears below the form with the short URL, a copy button, and a QR code.

**Feature cards:** Six cards highlighting key features — Fast Redirects, Click Analytics, Custom Aliases, QR Codes, Link Expiration, and Secure Authentication.

**Footer:** Copyright and attribution.

### Login Page (/login)

A clean login form with email and password fields, a "Sign In" button, and a "Continue with Google" button for OAuth login. Includes a link to the signup page.

### Signup Page (/signup)

Similar to the login page but with an additional "Confirm Password" field. After successful signup, the user is redirected to the login page with a message to check their email for confirmation.

### Dashboard Page (/dashboard)

A table showing all of the user's shortened links. Each row displays the original URL (truncated), the short URL (with copy button), click count, creation date, and action buttons (analytics, delete). The table supports sorting by different columns and pagination for users with many links.

### Analytics Page (/analytics/:code)

A comprehensive analytics dashboard for a single link. It includes:
- A summary card showing total clicks and the short URL
- A line chart showing daily click trends over the selected time period
- A bar chart showing the top countries by clicks
- A pie chart showing the device breakdown (mobile vs desktop vs tablet)
- Progress bars showing the browser breakdown (Chrome, Safari, Firefox, etc.)
- A time period selector (7 days, 30 days, 90 days, or 365 days)

## 15.3 Design System

The UI follows a consistent dark theme with the following color palette:

**Background:** Slate-950 (very dark blue-gray) for the main background. Slate-800 with 50% opacity for card backgrounds.

**Text:** White for headings. Slate-300 for body text. Slate-400 for secondary text. Slate-500 for placeholder text.

**Accent:** Indigo-600 for primary buttons and interactive elements. Indigo-400 for links and highlights. A gradient from indigo to blue for the logo and hero text.

**Borders:** Slate-700 with 50% opacity for card borders and dividers.

This color scheme provides excellent readability on the dark background and a modern, professional appearance.

## 15.4 Responsive Design

All pages are responsive, meaning they work on screens of all sizes (desktop, tablet, mobile). This is achieved using TailwindCSS responsive prefixes:

- No prefix: applies to all screen sizes (mobile-first)
- `sm:` applies at 640px and above (small tablets)
- `md:` applies at 768px and above (tablets)
- `lg:` applies at 1024px and above (laptops)
- `xl:` applies at 1280px and above (desktops)

For example, the dashboard table switches to a card layout on mobile screens, and the analytics charts stack vertically instead of appearing side by side.

## 15.5 State Management

The application uses React's built-in state management (useState, useEffect) and React Context for global state:

**AuthContext:** Provides authentication state (user, session, loading) and authentication functions (signUp, signIn, signOut, signInWithGoogle) to all components. Any component can access the current user by calling useAuth().

**Local component state:** Each page manages its own data state. For example, the Dashboard page has state for the list of links, loading status, current sort order, and current page number.


# 16. Workflow and Data Flow

## 16.1 Complete User Journey

Here is the complete workflow for a typical user:

### Journey 1: Anonymous User Shortens a URL

1. User visits https://2goi.in
2. Browser loads the React SPA (HTML, JS, CSS)
3. User pastes a long URL into the form
4. User clicks "Shorten URL"
5. Frontend sends POST /api/shorten with the URL
6. Backend validates the URL, generates a short code, caches it, generates QR code
7. Backend returns the short URL and QR code
8. Frontend displays the short URL with a copy button and QR code
9. User copies the short URL and shares it

### Journey 2: Visitor Clicks a Short Link

1. Someone receives the short link: https://2goi.in/2Bq
2. They click or type it in their browser
3. Browser sends GET /2Bq to our server
4. FastAPI's redirect router checks Redis for "url:2Bq"
5. Cache hit: Redis returns the original URL in 3ms
6. FastAPI sends HTTP 302 redirect to the original URL
7. Browser loads the original page
8. Meanwhile, a background task logs the click (browser, device, country, IP hash)

### Journey 3: User Signs Up and Views Analytics

1. User visits https://2goi.in/signup
2. Enters email and password, clicks "Create Account"
3. Frontend calls Supabase Auth signUp
4. Supabase sends a confirmation email via Resend
5. User opens email and clicks the confirmation link
6. User goes to /login and signs in
7. Supabase returns a JWT token
8. User is redirected to /dashboard
9. Frontend sends GET /api/links with the JWT token
10. Backend verifies the token, queries the database for the user's links
11. Dashboard displays a table of links with click counts
12. User clicks "Analytics" on a link
13. Frontend sends GET /api/analytics/2Bq with the JWT token
14. Backend queries analytics data (total clicks, countries, devices, browsers, daily trend)
15. Analytics page displays charts and breakdowns

## 16.2 Data Flow Diagram: Creating a Short Link

```
User                    Frontend              Backend               Database           Redis
  |                        |                     |                     |                  |
  |-- Paste URL ---------->|                     |                     |                  |
  |                        |                     |                     |                  |
  |-- Click "Shorten" ---->|                     |                     |                  |
  |                        |-- POST /api/shorten-->|                     |                  |
  |                        |                     |-- INSERT link ------>|                  |
  |                        |                     |<-- sequence_id ------|                  |
  |                        |                     |                     |                  |
  |                        |                     |-- encode_base62() --|                  |
  |                        |                     |                     |                  |
  |                        |                     |-- UPDATE short_code->|                  |
  |                        |                     |                     |                  |
  |                        |                     |-- SET url:code -----|----------------->|
  |                        |                     |                     |                  |
  |                        |                     |-- generate QR -----|                  |
  |                        |                     |                     |                  |
  |                        |<-- short_url + QR --|                     |                  |
  |                        |                     |                     |                  |
  |<-- Display result -----|                     |                     |                  |
```

## 16.3 Data Flow Diagram: Redirect (Cache Hit)

```
Visitor                 Server                 Redis
  |                        |                     |
  |-- GET /2Bq ----------->|                     |
  |                        |-- GET "url:2Bq" --->|
  |                        |<-- original URL ----|
  |<-- 302 Redirect -------|                     |
  |                        |                     |
  |                   [Background Task]          |
  |                        |-- INSERT click ---> DB
  |                        |-- UPSERT daily --> DB
  |                        |-- UPDATE count --> DB
```

## 16.4 Data Flow Diagram: Redirect (Cache Miss)

```
Visitor                 Server                 Redis              Database
  |                        |                     |                    |
  |-- GET /2Bq ----------->|                     |                    |
  |                        |-- GET "url:2Bq" --->|                    |
  |                        |<-- NULL (miss) -----|                    |
  |                        |                     |                    |
  |                        |-- SELECT original_url ------------------>|
  |                        |<-- original URL ------------------------|
  |                        |                     |                    |
  |                        |-- SET "url:2Bq" --->|                    |
  |                        |                     |                    |
  |<-- 302 Redirect -------|                     |                    |
  |                        |                     |                    |
  |                   [Background Task]          |                    |
  |                        |-- INSERT click -----|-------------------->|
```
# 17. Deployment and DevOps

## 17.1 Docker Containerization

The application is packaged as a Docker container using a multi-stage build. Multi-stage builds are a Docker feature that allows you to use multiple FROM statements in a single Dockerfile. Each FROM starts a new build stage, and you can selectively copy files from one stage to another.

**Stage 1: Build the React Frontend**

The first stage uses a Node.js image to install npm dependencies and build the React application. The build process compiles JSX to JavaScript, bundles all modules, minifies the code, and outputs static HTML, CSS, and JavaScript files in a "dist" folder.

Environment variables for the frontend (Supabase URL, anon key) are set as ENV statements in the Dockerfile. Vite embeds these variables at build time, meaning they become part of the compiled JavaScript bundle. This is important: changing these variables requires a rebuild, not just a restart.

**Stage 2: Set Up the Python Backend**

The second stage uses a Python image. It installs system dependencies (gcc, libpq-dev for PostgreSQL driver), installs Python dependencies from requirements.txt, copies the backend application code, and copies the built frontend from Stage 1 into the backend's static directory.

The final image contains only Python and the built frontend files. Node.js is not included in the final image, which keeps the image smaller.

**Why multi-stage builds?**

Without multi-stage builds, the final Docker image would contain both Node.js and Python runtimes, plus all build tools and node_modules. This would be a very large image (possibly over 1 GB). With multi-stage builds, the final image only contains what is needed at runtime, resulting in a much smaller image (approximately 300-400 MB).

## 17.2 Gunicorn and Uvicorn

The application runs with Gunicorn as the process manager and Uvicorn as the ASGI server.

**Gunicorn** manages multiple worker processes. If a worker crashes (due to an unhandled exception or out-of-memory), Gunicorn automatically restarts it. Gunicorn also distributes incoming requests across workers.

**Uvicorn** is an ASGI (Asynchronous Server Gateway Interface) server. It handles the async nature of FastAPI, allowing a single worker to handle many concurrent requests without blocking.

We run 4 Uvicorn workers. This means the application can handle 4 truly concurrent operations. Within each worker, the async nature of FastAPI allows handling many more concurrent I/O-bound operations (like database queries and Redis lookups).

The command is:
```
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
```

## 17.3 Render Deployment

Render is the cloud platform where the application is hosted. We chose Render because it offers free Docker deployment, free Redis, free SSL certificates, and auto-deployment from GitHub.

**Blueprint deployment:** Render reads our render.yaml file, which defines two services:
1. A web service (Docker) that runs our application
2. A Redis service for caching

The web service is configured with environment variables for database connections, Supabase credentials, and application settings. Secret variables (like database passwords) are set manually in the Render dashboard and are never committed to Git.

**Auto-deployment:** Every time we push code to the master branch on GitHub, Render automatically:
1. Detects the push
2. Pulls the latest code
3. Builds a new Docker image using our Dockerfile
4. Deploys the new image
5. Runs the health check (/api/health) to verify the new deployment is working
6. Switches traffic to the new deployment
7. Stops the old deployment

This process takes approximately 3 to 5 minutes. If the health check fails, Render rolls back to the previous working deployment.

**Free tier limitations:**
- The application sleeps after 15 minutes of inactivity
- The first request after sleeping takes 30 to 60 seconds (cold start)
- 750 free hours per month (enough for one service running continuously)
- No persistent disk storage

## 17.4 Custom Domain and SSL

**Domain setup:** The domain 2goi.in is registered on GoDaddy. DNS records point the domain to Render's infrastructure:
- An A record maps 2goi.in to Render's load balancer IP (216.24.57.1)
- A CNAME record maps www.2goi.in to twogoi.onrender.com

**SSL certificate:** Render automatically provisions and renews SSL certificates using Let's Encrypt. This means all traffic to 2goi.in is encrypted with HTTPS. Users never see a "not secure" warning in their browser.

## 17.5 Continuous Integration and Deployment (CI/CD)

Our CI/CD pipeline is simple but effective:

1. Developer makes code changes locally
2. Developer commits and pushes to GitHub (master branch)
3. Render detects the push and starts a new build
4. Docker multi-stage build compiles frontend and backend
5. New container is deployed with health check verification
6. Traffic switches to the new deployment

There is no separate CI step (like running tests) because the free tier does not support custom build scripts. Testing is done locally before pushing.


# 18. Challenges Faced and Solutions

## 18.1 Challenge: Supabase IPv6-Only Database

**Problem:** Supabase databases are IPv6-only for direct connections. Render's free tier only supports IPv4. This meant our application could not connect to the database.

**How we discovered it:** After deploying to Render, the health check endpoint reported "database: disconnected". The error logs showed connection timeout errors.

**Solution:** We switched from direct database connections to Supabase's Session Pooler. The Session Pooler provides an IPv4 endpoint that proxies connections to the IPv6 database. The connection string format changes from:
```
postgresql://db.supabase.co:5432/postgres
```
to:
```
postgresql://aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

**Lesson learned:** Always check the network compatibility between your hosting provider and database provider before deployment. IPv6 compatibility is often overlooked.

## 18.2 Challenge: ES256 JWT Verification

**Problem:** Supabase tokens are signed with ES256 (Elliptic Curve Digital Signature Algorithm), but most JWT tutorials and libraries default to HS256 (HMAC with SHA-256). Our initial implementation used HS256 and rejected all Supabase tokens.

**How we discovered it:** Users could log in (Supabase issued tokens), but every API call returned 401 Unauthorized. Decoding the token header revealed `"alg": "ES256"`, not HS256.

**Solution:** We implemented JWKS-based verification. Instead of using a shared secret (HS256), we fetch Supabase's public keys from their JWKS endpoint and use them to verify the ES256 signature. We also kept HS256 as a fallback for compatibility.

**Lesson learned:** Never assume the JWT algorithm. Always check the token's header to determine the correct verification method.

## 18.3 Challenge: Short Code Conflicts with Frontend Routes

**Problem:** Short codes like "login", "dashboard", or "signup" could conflict with frontend routes. If someone creates a custom alias "login", visiting 2goi.in/login would redirect instead of showing the login page.

**How we discovered it:** During testing, we realized that the redirect router could potentially match any URL path, including frontend routes.

**Solution:** The redirect router explicitly queries the database for the short code. If the code does not exist in the database, the request falls through to the SPA fallback, which serves the React application. Additionally, we added validation to prevent custom aliases that match reserved words (like "api", "login", "signup", "dashboard", "analytics", "health").

**Lesson learned:** In single-domain architectures, routing priority and reserved words must be carefully managed.

## 18.4 Challenge: Race Conditions in Click Counting

**Problem:** When multiple clicks arrive simultaneously for the same link, the click_count could be updated incorrectly. For example, if two requests read click_count = 5 at the same time, both would update it to 6 instead of 7.

**How we discovered it:** This is a well-known concurrency issue. We anticipated it during design.

**Solution:** We use atomic database operations. Instead of reading the count and then writing the new count (read-modify-write, which is vulnerable to race conditions), we use a single SQL statement:
```sql
UPDATE links SET click_count = click_count + 1 WHERE id = :link_id
```
PostgreSQL executes this atomically. Even if 100 concurrent requests run this statement, each one correctly increments the count. The same applies to the daily_click_stats upsert, which uses ON CONFLICT DO UPDATE.

**Lesson learned:** Always use atomic operations for counters and aggregations. Never use read-modify-write patterns in concurrent systems.

## 18.5 Challenge: Cold Starts on Render Free Tier

**Problem:** Render's free tier puts the application to sleep after 15 minutes of inactivity. The first request after sleeping takes 30 to 60 seconds because the Docker container needs to start, Python needs to load, and database connections need to be established.

**How we discovered it:** Users reported that the site was "slow" when they first visited it after a period of inactivity.

**Solution:** We solved this comprehensively using multiple approaches:
1. **UptimeRobot monitoring (primary fix):** Set up UptimeRobot (free service) to ping `GET /api/health` every 5 minutes. Since Render only sleeps after 15 minutes of inactivity, these pings keep the container permanently awake — eliminating cold starts entirely.
2. Optimizing the Docker image to reduce startup time (in case of restarts)
3. Using connection pooling so database connections are established quickly
4. Adding HEAD method support to the health endpoint for compatibility with all monitoring tools

With UptimeRobot in place, the site now stays alive 24/7 with zero cold starts.

**Lesson learned:** Free hosting tiers have trade-offs, but they can often be mitigated with creative solutions. UptimeRobot's free health pings completely solve Render's cold start problem. This is a common pattern used by developers worldwide to keep free-tier services alive.

## 18.6 Challenge: Google OAuth Callback Configuration

**Problem:** Google OAuth requires exact match on redirect URIs. If the callback URL in Google Cloud Console does not exactly match the one Supabase sends, Google rejects the authentication request with a "redirect_uri_mismatch" error.

**How we discovered it:** Users clicking "Continue with Google" were redirected to Google but then saw an error page instead of being logged in.

**Solution:** We carefully copied the exact callback URL from Supabase's Google provider settings and added it to Google Cloud Console's authorized redirect URIs. The URL must include the protocol (https://), the exact domain (svggdrykoxktgoimrqny.supabase.co), and the exact path (/auth/v1/callback).

**Lesson learned:** OAuth redirect URIs must match exactly. Even a trailing slash difference causes failure.

## 18.7 Challenge: Email Delivery for Signup Confirmation

**Problem:** Supabase's built-in email service has severe rate limits (3 emails per hour). This was insufficient for even basic testing, and emails were often delayed or not delivered.

**How we discovered it:** During testing, signup confirmation emails either did not arrive or took hours to arrive.

**Solution:** We integrated Resend as a custom SMTP provider. Resend offers 3,000 emails per month on the free tier, which is more than sufficient. We configured our own domain (2goi.in) in Resend, added DNS records (DKIM, SPF, MX) in GoDaddy, and connected Resend to Supabase as a custom SMTP provider. Emails now arrive within 1 to 5 minutes and come from noreply@2goi.in instead of a generic Supabase address.

**Lesson learned:** For any production application, always use a dedicated email service instead of relying on your authentication provider's built-in email delivery.

## 18.8 Challenge: DNS Propagation Delays

**Problem:** After adding DNS records in GoDaddy (for Render, Google Search Console, and Resend), the records were not immediately visible. Google Search Console could not verify domain ownership, and Resend could not verify the domain.

**How we discovered it:** Verification attempts failed with "record not found" errors even though we had correctly added the records.

**Solution:** We waited. DNS propagation can take from a few minutes to 48 hours, depending on the DNS provider and the type of record. In our case, most records propagated within 15 to 30 minutes. We used https://dnschecker.org to monitor propagation progress.

**Lesson learned:** DNS changes are not instant. Always plan for propagation delays when configuring domains.

## 18.9 Challenge: Corporate Firewall Blocking

**Problem:** The website was inaccessible from a corporate laptop because the company's web security proxy (Zscaler) blocked 2goi.in as an "uncategorized" website.

**How we discovered it:** Accessing the site from a corporate network showed a Zscaler block page instead of the website.

**Solution:** This is not a technical issue with the application. New websites are often blocked by corporate web filters until they are categorized. The options are: requesting the IT team to whitelist the domain, submitting the site for review through the block page, or accessing the site from a personal device or non-corporate network.

**Lesson learned:** Corporate firewalls can block new websites. This is outside the developer's control but should be considered when sharing the project with others in corporate environments.

## 18.10 Challenge: Duplicate Email Signup Silently Accepted

**Problem:** When a user tried to sign up with an email that already existed in Supabase, the system did not show an error. Instead, Supabase returned a "fake" success response with an empty `identities` array. The user saw a "Check your email" success message, but no confirmation email was sent (because the account already existed). This confused users who thought they created a new account.

**How we discovered it:** During testing, signing up with the same email twice showed a success toast both times. Checking the Supabase users table confirmed only one entry existed, but the UI gave no indication of a duplicate.

**Root cause:** Supabase intentionally does not return an error for duplicate signups. This is a security feature to prevent email enumeration attacks (where an attacker could discover which emails are registered by trying to sign up). Instead, Supabase returns `data.user.identities = []` (an empty array) when the email already exists.

**Solution:** We added a check in the `signUp()` function in `AuthContext.jsx`:
```javascript
const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
    // Supabase returns a fake user with empty identities if email already exists
    if (data?.user?.identities?.length === 0) {
        throw new Error('An account with this email already exists. Please sign in instead.')
    }
    return data
}
```

Additionally, in `SignupPage.jsx`, when this specific error is detected, the user is automatically redirected to the login page with a clear error toast message.

**Lesson learned:** Always check your authentication provider's documentation for edge-case behaviors. Supabase's duplicate email handling is by design, but the UI must compensate by detecting the `identities` array and showing a user-friendly message.

## 18.11 Challenge: Manually Typed URLs Without Protocol Fail

**Problem:** When a user manually typed a URL like `www.google.com` or `google.com` into the shortener input box (instead of pasting a full URL), clicking Shorten showed "Failed to shorten URL". The backend's Pydantic validator requires URLs to start with `http://` or `https://`, but users rarely type the protocol when entering URLs manually.

**How we discovered it:** Testing the form by typing `www.google.com` manually (without pasting) and clicking Shorten returned an error.

**Solution:** We added a simple URL normalization step in `ShortenForm.jsx` that auto-prepends `https://` if the user's input doesn't already include a protocol:
```javascript
let finalUrl = url.trim()
if (!/^https?:\/\//i.test(finalUrl)) {
    finalUrl = 'https://' + finalUrl
}
```

Now all these inputs work:
- `google.com` → becomes `https://google.com`
- `www.google.com` → becomes `https://www.google.com`
- `https://google.com` → unchanged (already has protocol)
- `http://example.com` → unchanged (already has protocol)

**Lesson learned:** Never assume users will provide perfectly formatted input. Always normalize user input on the frontend before sending it to the backend. This is a basic UX principle — the application should be forgiving and helpful, not strict and punishing.

## 18.12 Challenge: Render Free Tier Cold Starts (30-60 Second Delays)

**Problem:** Render's free tier puts the Docker container to sleep after 15 minutes of inactivity. When the next user visits the site, they experience a 30-60 second cold start while:
1. Render spins up the Docker container
2. Python loads FastAPI and all dependencies
3. Database connection pool is established
4. Redis connection is established

This made the site appear broken or extremely slow to new visitors.

**How we discovered it:** Users reported that the site was "down" or "taking forever to load" when they visited after a period of inactivity. Checking the Render dashboard confirmed the service was sleeping.

**Why cookies cannot solve this:** Cookies are stored in the user's browser (client-side). The cold start problem is server-side — Render's container is shut down. No amount of browser-side storage can prevent a server from sleeping. The only solution is to send real HTTP requests to keep the server awake.

**Solution:** We set up **UptimeRobot** (free monitoring service) to ping the health endpoint every 5 minutes:

- **URL monitored:** `https://2goi.in/api/health`
- **Ping interval:** Every 5 minutes
- **What it does:** Sends a real HTTP `GET` request to the health endpoint, which forces Render to keep the container running since it sees activity every 5 minutes (well within the 15-minute idle threshold)

### How Render and UptimeRobot Work Together

| Tool | Role | What It Does |
|------|------|--------------|
| **Render** | Hosting | Runs the Docker container, serves the app, provides the URL |
| **UptimeRobot** | Monitoring | Sends HTTP pings every 5 min to prevent Render from sleeping the container |

### Render Challenges Fixed by UptimeRobot

| Render Free Tier Problem | How UptimeRobot Fixes It |
|--------------------------|-------------------------|
| Service sleeps after 15 min inactivity | Pings every 5 min — service never goes idle |
| First request after sleep takes 30-60 sec (cold start) | No cold starts — container stays warm 24/7 |
| Health checks fail during sleep | Continuous pings keep health checks green |
| Users think the site is broken/slow | Site always responds instantly (~200-500ms) |

### Technical Detail: HEAD Method Support

During setup, UptimeRobot initially returned a 405 (Method Not Allowed) error because it was sending HTTP `HEAD` requests, but our health endpoint only accepted `GET`. We fixed this by changing the health endpoint from:
```python
@router.get("/api/health")
```
to:
```python
@router.api_route("/api/health", methods=["GET", "HEAD"])
```

This ensures compatibility with all monitoring tools, not just UptimeRobot.

### UptimeRobot Setup Steps

1. Create a free account at https://uptimerobot.com
2. Click **"+ New"** → Select **HTTP(s)** monitor
3. Set URL to `https://2goi.in/api/health`, interval to 5 minutes
4. Enable email notifications
5. Save — monitor turns green within 5-10 minutes

### Bonus Benefits

- **Uptime tracking:** Shows 99.9%+ uptime percentage (great for resume)
- **Response time graphs:** Visualize API performance over time
- **Downtime alerts:** Get emailed instantly if the site goes down
- **Cost:** Completely free (supports up to 50 monitors)

**Lesson learned:** Free hosting tiers have trade-offs. Render's free tier is excellent for academic projects but requires a keep-alive strategy. UptimeRobot provides this for free while also adding professional uptime monitoring capabilities. This is a common pattern used by developers worldwide to keep free-tier services alive.

## 18.13 Challenge: Password Field Usability — No Visibility Toggle

**Problem:** The password fields on the Login and Signup pages used `type="password"`, which permanently masks the input. Users had no way to verify what they typed, leading to failed login attempts (typos) and mismatched passwords during signup.

**Solution:** Added an eye icon toggle button to every password field using Lucide's `Eye` and `EyeOff` icons:

- **Login page:** 1 toggle (password field)
- **Signup page:** 2 independent toggles (password + confirm password)

The implementation toggles `type="password"` to `type="text"` on click. Key details:
- `type="button"` on the toggle prevents accidental form submission
- `tabIndex={-1}` prevents the toggle from interfering with keyboard Tab navigation
- `pr-10` padding on the input ensures typed text does not overlap the icon
- Each field has its own independent state (`showPassword`, `showConfirmPassword`)

**Lesson learned:** Small UX details like password visibility toggles significantly improve usability. Modern users expect this feature — most major websites (Google, GitHub, Amazon) include it. Always consider the user's experience with form inputs.


# 19. Scalability and World-Wide Challenges

This section discusses how the system would need to evolve to handle millions of users worldwide. While our current deployment handles our academic use case, understanding scalability challenges demonstrates deep system design knowledge.

## 19.1 Current System Capacity

### Realistic Limits (Free Tier)

| Metric | Estimate | Bottleneck |
|--------|----------|-----------|
| Concurrent users | ~50-100 | 512 MB RAM (Render) |
| Redirects per second | ~100-200 | Redis cache hit = sub-5ms |
| Link creation per second | ~10-20 | DB write + Base62 + QR |
| Total stored links | ~2-3 million | Supabase 500 MB |
| Redis cached URLs | ~170,000 | 25 MB / ~150 bytes each |
| DB connection pool | 20 + 10 overflow | Max 30 concurrent |

### Rate Limits

| User Type | Limit | Window | Implementation |
|-----------|-------|--------|----------------|
| Anonymous | 100 requests/min | Per IP | SlowAPI |
| Authenticated | 1000 requests/min | Per IP | SlowAPI |

When limit hit: HTTP 429 "Too Many Requests". Resets after sliding window expires.

### Session & Usage Limits

- **Links lifetime:** Permanent by default, or user-set expiration
- **No session timeout** for dashboard usage
- **Anonymous shortening:** No login required, no limit per session
- **Authenticated:** Full dashboard, analytics, custom aliases, soft delete

### Free-Tier Resource Usage

| Service | Free Tier Limit | Our Usage | Headroom |
|---------|----------------|-----------|----------|
| Render Web Service | 512 MB RAM, shared CPU | ~80-100 MB | ~80% free |
| Render Redis | 25 MB storage | ~1-5 MB | ~80-96% free |
| Supabase PostgreSQL | 500 MB storage | ~few MB | >99% free |
| Supabase Auth | 50,000 MAU | <100 | >99% free |
| Resend Email | 3,000 emails/month | <50 | >98% free |
| UptimeRobot | 50 monitors | 1 | 49 remaining |

### What Happens at Capacity?

- **512 MB RAM hit:** Gunicorn workers slow down → Render kills container → auto-restart (stateless, no data loss)
- **Redis 25 MB hit:** LRU eviction kicks in → oldest cache entries removed → more DB fallback
- **Supabase 500 MB hit:** New link creation fails → existing links and redirects still work (cached)
- **Rate limit hit:** HTTP 429 response → user must wait for window to slide

This is appropriate for a portfolio project but would not handle millions of users.

## 19.2 Challenge: Handling Millions of Redirects Per Second

**The problem:** If 2GOI became as popular as Bitly, it might need to handle millions of redirect requests per second. Our single server with 4 workers cannot handle this load.

**Solution: Horizontal Scaling**

Instead of one big server (vertical scaling), we would deploy many identical servers behind a load balancer:

```
                 Internet
                    |
             Load Balancer
            /   |    |    \
          S1   S2   S3   S4    (Multiple identical servers)
           \   |    |    /
            Redis Cluster       (Shared cache)
            /   |    |    \
          DB1  DB2  DB3  DB4    (Database replicas)
```

Each server runs the same Docker image. The load balancer distributes requests evenly across servers. All servers share the same Redis cluster and database, so any server can handle any request.

**Key considerations:**
- Servers must be stateless (no data stored in memory between requests). Our architecture already supports this because all state is in PostgreSQL and Redis.
- Session stickiness is not needed because JWT tokens are self-contained.
- Auto-scaling can add or remove servers based on traffic patterns.

## 19.3 Challenge: Database Bottleneck

**The problem:** As the number of links and clicks grows to billions, a single PostgreSQL instance becomes a bottleneck. Queries slow down, and write throughput is limited.

**Solution: Database Sharding and Read Replicas**

**Read replicas:** Create read-only copies of the database. Redirect lookups (reads) go to replicas, while link creation (writes) goes to the primary. Since reads vastly outnumber writes, this dramatically reduces load on the primary database.

```
Write requests  ---->  Primary DB
Read requests   ---->  Replica 1 / Replica 2 / Replica 3
```

**Database sharding:** Split the data across multiple database instances based on a shard key. For example, links could be sharded by the first character of the short code:
- Links starting with 0-9 go to Shard 1
- Links starting with a-m go to Shard 2
- Links starting with n-z go to Shard 3
- Links starting with A-Z go to Shard 4

Each shard handles a fraction of the total data, so queries are faster and storage is distributed.

## 19.4 Challenge: Redis Cache at Scale

**The problem:** A single Redis instance has limited memory (25 MB on our free tier, but even paid Redis has limits). With billions of links, we cannot cache them all.

**Solution: Redis Cluster**

A Redis Cluster distributes data across multiple Redis nodes. The cluster automatically shards data using consistent hashing. If one node fails, the cluster continues operating with the remaining nodes.

**Additional optimization: Tiered caching**

```
Request → L1 Cache (in-process memory, microseconds)
       → L2 Cache (Redis, milliseconds)
       → L3 (Database, tens of milliseconds)
```

The L1 cache is a small in-memory cache within each server process. It holds the most frequently accessed URLs (the "hot" links). This avoids even the Redis network round-trip for the most popular links.

## 19.5 Challenge: Collision Prevention at Global Scale

**The problem:** Our current system uses a single PostgreSQL sequence for generating IDs. This works on a single database but does not work across multiple sharded databases. Each shard would need its own sequence, and sequences from different shards could collide.

**Solution: Distributed ID Generation**

Several approaches exist:

**Snowflake IDs (used by Twitter):** Generate 64-bit IDs that include a timestamp, machine ID, and sequence number. Each machine generates unique IDs without coordination.

**ID ranges:** Assign non-overlapping ID ranges to each shard. Shard 1 gets IDs 1 to 1 billion, Shard 2 gets 1 billion to 2 billion, and so on. When a shard exhausts its range, it requests a new range from a central coordinator.

**UUIDs with Base62:** Generate a random UUID, encode it in Base62, and use a longer short code (8 to 10 characters). The probability of collision with 128-bit UUIDs is astronomically low.

## 19.6 Challenge: Global Latency

**The problem:** If the server is in Mumbai (India) and a user in New York clicks a short link, the request travels across the ocean, adding 200 to 300 milliseconds of latency.

**Solution: Content Delivery Network (CDN) and Edge Computing**

Deploy Redis caches (or even lightweight redirect services) at edge locations around the world. When a user in New York clicks a link, the request goes to the nearest edge location (perhaps in Virginia), which serves the redirect from its local cache. Only cache misses need to reach the origin server.

Services like Cloudflare Workers, AWS CloudFront, or Fastly can implement this pattern.

```
User in New York  →  Edge (Virginia)  →  Cache HIT → Redirect (5ms)
                                      →  Cache MISS → Origin (Mumbai) → Redirect (250ms, then cached)
```

## 19.7 Challenge: Hot Links

**The problem:** A viral link might receive millions of clicks per minute. Even with caching, the load on a single Redis node could be overwhelming.

**Solution: Hot link detection and special handling**

1. Monitor click rates in real-time
2. When a link exceeds a threshold (say, 10,000 clicks per minute), mark it as "hot"
3. Replicate the hot link's cache entry to all Redis nodes
4. Use the L1 in-process cache to serve hot links without any network calls

This ensures that the most popular links are served with the absolute minimum latency, even under extreme load.

## 19.8 Challenge: Analytics at Scale

**The problem:** With billions of clicks, the clicks table becomes enormous. Even with pre-aggregated daily stats, the raw click data is needed for detailed breakdowns (country, browser, device).

**Solution: Data warehouse and stream processing**

Move analytics data from the real-time database to a data warehouse:

```
Click event → Kafka (message queue) → PostgreSQL (real-time, last 7 days)
                                    → ClickHouse (data warehouse, all historical data)
```

ClickHouse (or similar column-oriented databases) can query billions of rows in seconds for analytics. The PostgreSQL database only keeps recent data, keeping it fast for real-time operations.

## 19.9 Scalability Summary Table

| Challenge | Current Solution | Scaled Solution |
|-----------|-----------------|-----------------|
| Traffic | Single server, 4 workers | Horizontal scaling with load balancer |
| Database reads | Single instance | Read replicas |
| Database writes | Single instance | Sharding by short code prefix |
| Cache size | Single Redis, 25MB | Redis Cluster across multiple nodes |
| ID generation | PostgreSQL SEQUENCE | Snowflake IDs or ID ranges |
| Global latency | Single region (Mumbai) | CDN with edge caching |
| Hot links | Redis cache | L1 in-process cache + replicated Redis |
| Analytics storage | PostgreSQL | Data warehouse (ClickHouse) |
| Message handling | Synchronous | Apache Kafka for async processing |


# 20. Fault Tolerance and Failover

## 20.1 What is Fault Tolerance?

Fault tolerance is the ability of a system to continue operating when one or more components fail. In a production system, failures are inevitable. Servers crash, networks go down, databases become unavailable, and caches run out of memory. A well-designed system handles these failures gracefully.

## 20.2 Redis Failure

**What happens:** Redis becomes unavailable (server crash, network issue, out of memory).

**Impact:** Redirect response times increase from 3 to 5 milliseconds to 20 to 50 milliseconds (database fallback). No data is lost because Redis is only a cache — the source of truth is always PostgreSQL.

**How we handle it:** Every Redis operation is wrapped in try-except blocks. If any Redis call fails, the code catches the exception and continues without caching. The get_redis() function returns None when Redis is unavailable, and all calling code checks for None before attempting Redis operations.

**Recovery:** When Redis comes back online, the cache is initially empty. As users click short links, cache misses cause database lookups, and the results are stored in Redis. The cache gradually warms up to normal levels within minutes.

## 20.3 Database Failure

**What happens:** PostgreSQL becomes unavailable (Supabase outage, network issue).

**Impact:** This is the most severe failure. Link creation, analytics, and user authentication all fail. However, redirects for cached links still work because they can be served from Redis.

**How we handle it:** The health check endpoint (/api/health) reports the database as "disconnected". API endpoints that require database access return appropriate error responses (503 Service Unavailable). The frontend displays error messages to the user.

**Recovery:** When the database comes back online, the application automatically reconnects using the connection pool. No manual intervention is needed. SQLAlchemy's connection pool handles reconnection transparently.

## 20.4 Application Server Crash

**What happens:** A Gunicorn worker process crashes due to an unhandled exception or out-of-memory error.

**Impact:** Requests being processed by that worker fail. Other workers continue handling requests normally.

**How we handle it:** Gunicorn automatically restarts crashed workers. The --graceful-timeout 30 setting gives dying workers 30 seconds to finish in-flight requests before being killed.

**Recovery:** Gunicorn detects the crashed worker and spawns a new one within seconds. Users experience a brief interruption (a single failed request) at most.

## 20.5 Complete Server Failure

**What happens:** The entire Render service goes down (infrastructure failure).

**Impact:** The website is completely unavailable. All requests fail.

**How we handle it:** Render monitors the health check endpoint. If it fails repeatedly, Render attempts to restart the service. If the issue persists, Render's infrastructure team investigates.

**Recovery:** Render automatically redeploys the last working version. Since our application is stateless (all data is in PostgreSQL and Redis), a fresh deployment immediately works with all existing data.

## 20.6 Supabase Auth Failure

**What happens:** Supabase's authentication service goes down.

**Impact:** New logins and signups fail. However, users who are already logged in can continue using the API because their JWT tokens are verified locally (using cached JWKS keys). The tokens remain valid until they expire (1 hour).

**How we handle it:** The JWKS keys are cached by the JWT library. Even if the JWKS endpoint is temporarily unavailable, recently fetched keys can still verify tokens.

**Recovery:** When Supabase Auth comes back online, the JWKS cache is refreshed on the next verification request. New logins work immediately.

## 20.7 Failure Cascade Prevention

A "failure cascade" occurs when one component's failure causes other components to fail. For example, if Redis goes down and all requests suddenly hit the database, the database might become overloaded and fail too.

We prevent cascades through:
1. **Circuit breakers** (conceptual): If Redis is down, we stop trying to connect to it after a few failures instead of attempting connection on every request.
2. **Connection pooling**: The database connection pool limits the number of concurrent connections, preventing the database from being overwhelmed.
3. **Rate limiting**: Even during failures, rate limiting prevents any single user from overwhelming the system.
4. **Graceful degradation**: Each component can fail independently without taking down the entire system.

## 20.8 Fault Tolerance Summary

| Component | Failure Impact | Recovery Mechanism | Time to Recover |
|-----------|---------------|-------------------|-----------------|
| Redis | Slower redirects (20-50ms) | Automatic fallback to DB | Instant |
| Database | Link creation and analytics fail | Auto-reconnect via pool | Seconds to minutes |
| Worker process | Single request fails | Gunicorn auto-restarts | Seconds |
| Entire server | Site down | Render auto-redeploys | Minutes |
| Supabase Auth | New logins fail | Cached JWKS keys | Minutes to hours |
| Resend (Email) | Confirmation emails delayed | Retry queue | Minutes |


# 21. Security Analysis

## 21.1 Authentication Security

**JWT token verification:** All API requests that require authentication include a JWT token in the Authorization header. The backend verifies the token using Supabase's public keys (ES256 algorithm). Tokens cannot be forged without Supabase's private key, which is never exposed.

**Token expiration:** Tokens expire after 1 hour. Even if a token is stolen, it has a limited lifespan. Supabase automatically handles token refresh using refresh tokens.

**OAuth security:** Google OAuth uses the Authorization Code flow, which is the most secure OAuth flow. The authorization code is exchanged for tokens on the server side (Supabase), so tokens never appear in the browser's URL bar.

## 21.2 Data Security

**No raw IP storage:** Visitor IP addresses are hashed with SHA-256 before storage. The original IP cannot be recovered from the hash.

**HTTPS everywhere:** All traffic is encrypted with TLS/SSL. Render automatically provisions and renews SSL certificates.

**Environment variables:** All secrets (database passwords, API keys, JWT secrets) are stored as environment variables on the server. They are never committed to Git or exposed in the frontend.

**Service role key isolation:** Supabase's service_role key (which has admin access to the database) is only used on the backend. The frontend only has the anon key, which has restricted access enforced by Row Level Security.

## 21.3 Input Validation

**URL validation:** URLs are validated using Pydantic's HttpUrl type, which rejects malformed URLs and non-HTTP/HTTPS protocols. This prevents attacks like JavaScript injection through URLs (`javascript:alert('xss')`).

**Custom alias validation:** Custom aliases are restricted to alphanumeric characters, hyphens, and underscores using regex validation. This prevents SQL injection and path traversal attacks.

**Rate limiting:** Anonymous users are limited to 100 API requests per minute. Authenticated users get 1000 per minute. This prevents brute-force attacks, database spam, and denial-of-service attempts.

## 21.4 Common Attack Prevention

**SQL Injection:** We use SQLAlchemy ORM, which automatically parameterizes all queries. User input is never concatenated into SQL strings.

**Cross-Site Scripting (XSS):** React automatically escapes all content rendered in JSX, preventing XSS attacks. Additionally, Content-Security-Policy headers could be added for defense in depth.

**Cross-Site Request Forgery (CSRF):** Our API uses JWT tokens in the Authorization header (not cookies), which makes CSRF attacks impossible. CSRF attacks exploit cookie-based authentication, which we do not use.

**Open Redirect:** Short URLs always redirect to the stored original_url from the database. There is no user-controllable redirect parameter, so open redirect attacks are not possible.


# 22. Performance Analysis

## 22.1 Response Time Benchmarks

| Endpoint | Cache Hit | Cache Miss | Description |
|----------|-----------|------------|-------------|
| GET /{code} (redirect) | 3-5 ms | 20-50 ms | Core redirect operation |
| POST /api/shorten | N/A | 50-100 ms | Link creation (DB insert + QR generation) |
| GET /api/links | N/A | 30-80 ms | Dashboard data (paginated DB query) |
| GET /api/analytics/{code} | N/A | 50-150 ms | Analytics (multiple DB queries) |
| GET /api/health | N/A | 5-10 ms | Health check (DB + Redis ping) |

## 22.2 Why Redirects Are Fast

The redirect endpoint is optimized at every level:

1. **Redis cache:** The most common path (cache hit) requires only a single Redis GET command, which completes in 1 to 2 milliseconds. With network overhead, the total is 3 to 5 milliseconds.

2. **Database index:** For cache misses, the query uses the index on short_code, making it a single-row lookup by index. This is an O(log n) operation regardless of table size.

3. **Async click logging:** Click logging runs as a background task after the redirect response is sent. The user does not wait for click logging.

4. **Minimal response:** An HTTP 302 redirect response is just headers (no body). This minimizes the amount of data sent over the network.

## 22.3 Database Query Performance

**Efficient analytics with pre-aggregation:** The daily_click_stats table reduces analytics query time from O(total_clicks) to O(days). For a link with 1 million clicks over 30 days, the query reads 30 rows instead of 1 million rows. This is a 33,000x improvement.

**Pagination for the dashboard:** Instead of loading all links at once, the dashboard uses pagination (20 links per page). This bounds the query time regardless of how many links a user has.

**Connection pooling:** Reusing database connections eliminates the 50 to 100 millisecond overhead of establishing new connections.

## 22.4 Frontend Performance

**Vite production build:** The React application is compiled, minified, and bundled by Vite. Tree-shaking removes unused code. Code splitting loads only the JavaScript needed for the current page.

**TailwindCSS purging:** TailwindCSS removes all unused CSS classes from the production build, resulting in a very small CSS file (typically under 20 KB).

**Lazy loading:** Charts on the analytics page use React's lazy loading, so the Recharts library is only downloaded when the user visits the analytics page.


# 23. Testing

## 23.1 Manual Testing Performed

The following test cases were verified manually:

**URL Shortening:**
- Shorten a valid URL → short URL and QR code returned
- Shorten with custom alias → custom code used
- Shorten with duplicate alias → 409 error returned
- Shorten with invalid URL → 422 validation error
- Shorten with expiration → expires_at set correctly

**Redirects:**
- Click a valid short URL → 302 redirect to original
- Click an expired short URL → 410 Gone
- Click a non-existent short URL → 404 Not Found
- Click a deleted (inactive) short URL → 404 Not Found

**Authentication:**
- Sign up with email/password → account created, confirmation email sent
- Sign in with correct credentials → JWT token issued
- Sign in with wrong password → error message
- Sign in with unconfirmed email → appropriate error message
- Sign in with Google → redirects to Google, returns to dashboard
- Sign out → session cleared, redirected to home

**Dashboard:**
- View links list → shows all user's links
- Copy short URL → copies to clipboard
- Delete a link → link removed from list, redirect returns 404
- Sort by click count → links sorted correctly
- Pagination → next/previous pages work

**Analytics:**
- View analytics for a link → charts display correctly
- Change time period → data updates
- View analytics for another user's link → 403 forbidden

## 23.2 How to Test

For future testing, the following verification commands can be used:

```bash
# Health check
curl https://2goi.in/api/health

# Shorten a URL
curl -X POST https://2goi.in/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'

# Click a short URL (follow redirects)
curl -v -L https://2goi.in/2Bi

# Check robots.txt
curl https://2goi.in/robots.txt

# Check sitemap
curl https://2goi.in/sitemap.xml
```


## 23.3 Edge Case Testing Results

We systematically tested 35 edge cases across all major features to ensure the application handles unusual inputs and scenarios gracefully.

### URL Input Edge Cases (Frontend + Backend)

| # | Input | After Frontend Normalization | Backend Accepts? | Notes |
|---|-------|------------------------------|-----------------|-------|
| 1 | `www.google.com` | `https://www.google.com` | PASS | Auto-prepend `https://` |
| 2 | `google.com` | `https://google.com` | PASS | Bare domain |
| 3 | `https://google.com` | `https://google.com` | PASS | Already has protocol |
| 4 | `http://example.com` | `http://example.com` | PASS | HTTP preserved |
| 5 | `https://www.google.com/search?q=hello` | Unchanged | PASS | Query params work |
| 6 | `example.com/path/page` | `https://example.com/path/page` | PASS | Path without protocol |
| 7 | `https://localhost:3000` | Unchanged | PASS | Localhost with port |
| 8 | `192.168.1.1` | `https://192.168.1.1` | PASS | IP address |
| 9 | `HTTPS://GOOGLE.COM` | Unchanged | PASS | Case-insensitive |
| 10 | `google.com?q=test` | `https://google.com?q=test` | PASS | Query without protocol |
| 11 | (empty) | — | BLOCKED | Frontend prevents submit |
| 12 | (spaces only) | — | BLOCKED | Frontend prevents submit |
| 13 | `not a url` | `https://not a url` | REJECTED | Backend regex rejects — correct |
| 14 | `ftp://files.example.com` | `https://ftp://files...` | REJECTED | Non-HTTP protocols blocked — correct |
| 15 | `javascript:alert(1)` | `https://javascript:alert(1)` | REJECTED | XSS attempt blocked — correct |

**Key takeaway:** Valid URLs always pass (with or without protocol). Invalid input is always rejected by the backend's Pydantic regex validator. XSS and injection attempts are blocked.

### Redirect Router Edge Cases

| # | Scenario | Expected Behavior | Status |
|---|----------|-------------------|--------|
| 16 | Visit `/login`, `/signup`, `/dashboard` | SPA fallback serves React app | PASS |
| 17 | Visit `/api/health`, `/api/shorten` | Routed to API handlers | PASS |
| 18 | Visit `/assets/*` | Static files served | PASS |
| 19 | Visit non-existent short code (e.g., `/xyz123`) | 404 "Short URL not found" | PASS |
| 20 | Visit expired short code | 410 "This link has expired" | PASS |
| 21 | Redis down during redirect | Falls back to database query | PASS |
| 22 | Redis down during link creation | Link created, cache priming silently skipped | PASS |

**Key takeaway:** The redirect router correctly distinguishes between short codes, frontend routes, and API paths. Redis failures are handled gracefully — the app never crashes due to Redis being unavailable.

### Authentication Edge Cases

| # | Scenario | Expected Behavior | Status |
|---|----------|-------------------|--------|
| 23 | Signup with existing email | Error toast: "Account already exists" + redirect to login | PASS |
| 24 | Login with wrong password | Error toast from Supabase | PASS |
| 25 | Login with unconfirmed email | Specific error: "Please confirm your email" | PASS |
| 26 | Access `/dashboard` without login | Redirected to login page | PASS |
| 27 | API call with expired JWT | 401 Unauthorized | PASS |
| 28 | API call with no JWT (anonymous shorten) | Works — link created with no owner | PASS |

**Key takeaway:** All authentication edge cases are handled. Duplicate signups are caught by checking Supabase's `identities` array. Anonymous users can shorten URLs but cannot access the dashboard or analytics.

### Race Condition / Concurrency Edge Cases

| # | Scenario | How It Is Handled | Status |
|---|----------|-------------------|--------|
| 29 | Simultaneous clicks on same link | Atomic SQL: `SET click_count = click_count + 1` | PASS |
| 30 | Simultaneous daily stats updates | PostgreSQL `ON CONFLICT DO UPDATE` upsert | PASS |

**Key takeaway:** All counters use atomic database operations. There are no read-modify-write patterns, so race conditions cannot corrupt data even under heavy concurrent load.

### Custom Alias Edge Cases

| # | Scenario | Expected Behavior | Status |
|---|----------|-------------------|--------|
| 31 | Custom alias less than 3 characters | 422 Validation error | PASS |
| 32 | Custom alias with special characters (`@#$`) | 422 Validation error (only alphanumeric + hyphens) | PASS |
| 33 | Duplicate custom alias | 409 Conflict: "alias is already taken" | PASS |

### Data Integrity Edge Cases

| # | Scenario | Expected Behavior | Status |
|---|----------|-------------------|--------|
| 34 | Delete link → Redis cache invalidated | Redis entry for the short code is removed | PASS |
| 35 | Visit a soft-deleted link | 404 Not Found (query filters `is_active=True`) | PASS |

**Summary:** All 35 edge cases passed. The application correctly handles invalid input, race conditions, authentication edge cases, Redis failures, and XSS/injection attempts.


# 24. SEO and Discoverability

## 24.1 What is SEO?

SEO (Search Engine Optimization) is the practice of optimizing a website so that it appears in search engine results. When someone searches "URL shortener" on Google, we want 2goi.in to appear in the results.

## 24.2 SEO Implementations

**Meta tags:** The index.html file includes comprehensive meta tags:
- Title tag: "2GOI - Free URL Shortener | Shorten Links, Track Clicks & Generate QR Codes"
- Description: A detailed description of the service for search result snippets
- Keywords: Relevant keywords like "url shortener", "link shortener", "QR code generator"

**Open Graph tags:** These control how the site appears when shared on social media (Facebook, LinkedIn). They specify the title, description, image, and URL that appear in the link preview.

**Twitter Card tags:** Similar to Open Graph but specifically for Twitter/X. They define the card type, title, and description for Twitter link previews.

**Structured data (JSON-LD):** A machine-readable description of the website in JSON-LD format. This helps Google understand what the site is and can result in rich snippets in search results.

**Canonical URL:** Tells search engines the authoritative URL for the page, preventing duplicate content issues.

**Sitemap (sitemap.xml):** An XML file that lists all public pages on the site. Google's crawler reads this to discover all pages.

**Robots.txt:** A file that tells search engine crawlers which parts of the site to index and which to skip. We allow all crawlers to index public pages but block the /api/ paths.

## 24.3 Google Search Console

We registered the site with Google Search Console and verified ownership using a DNS TXT record. We submitted the sitemap and requested indexing. Google will start crawling and indexing the site within a few days to a few weeks.


# 25. Email System

## 25.1 Why Custom Email?

Supabase's built-in email service has severe limitations: only 3 emails per hour and 30 per day. For a production application, this is insufficient. Emails also come from a generic Supabase address, which looks unprofessional.

## 25.2 Resend Integration

We integrated Resend as a custom SMTP provider for Supabase Auth. Resend offers 3,000 emails per month on the free tier.

**Setup steps:**
1. Created a Resend account at resend.com
2. Added our domain (2goi.in) in Resend's dashboard
3. Added DNS records in GoDaddy for domain verification (DKIM, SPF, MX)
4. Created an API key in Resend
5. Configured Supabase's custom SMTP settings with Resend's SMTP credentials

**Result:** Signup confirmation emails are now sent from noreply@2goi.in, arriving within 1 to 5 minutes. The emails look professional and come from our own domain.


# 26. Cost Analysis

## 26.1 Monthly Cost Breakdown

| Service | Plan | Monthly Cost | What We Get |
|---------|------|-------------|-------------|
| Supabase | Free | 0 rupees | 500 MB database, 50,000 auth users, unlimited API requests |
| Render Web | Free | 0 rupees | 750 hours/month, auto-deploy, free SSL |
| Render Redis | Free | 0 rupees | 25 MB cache, LRU eviction |
| Resend | Free | 0 rupees | 3,000 emails/month |
| Google Cloud | Free | 0 rupees | OAuth is free, no usage limits |
| Google Search Console | Free | 0 rupees | Unlimited, forever |
| UptimeRobot | Free | 0 rupees | 50 monitors, 5-min interval, email alerts, uptime tracking |
| GoDaddy Domain | Paid | Approximately 67 rupees | Domain renewal (approximately 800 rupees/year) |
| **Total** | | **Approximately 67 rupees/month** | |

## 26.2 If We Needed to Scale

| Service | Paid Plan | Monthly Cost | What We Would Get |
|---------|-----------|-------------|-------------------|
| Supabase Pro | $25/month | Approximately 2,100 rupees | 8 GB database, 100,000 auth users, daily backups |
| Render Starter | $7/month | Approximately 590 rupees | Always-on (no sleep), more memory |
| Render Redis Pro | $10/month | Approximately 840 rupees | 256 MB cache, persistence |
| Resend Pro | $20/month | Approximately 1,680 rupees | 50,000 emails/month |
| **Scaled Total** | | **Approximately 5,277 rupees/month** | |


# 27. Future Enhancements

## 27.1 Short-Term Improvements

1. **Password reset flow:** Add a "Forgot Password" link on the login page that sends a password reset email
2. **Link editing:** Allow users to change the original URL of an existing short link
3. **Bulk shortening:** Allow users to upload a CSV of URLs and get short links in batch
4. **API key authentication:** Provide API keys for programmatic access (not just JWT)
5. **Dark/Light theme toggle:** Allow users to switch between dark and light themes

## 27.2 Medium-Term Features

1. **Custom domains:** Allow users to bring their own domains for branded short links
2. **Team workspaces:** Multiple users can collaborate on managing links
3. **A/B testing links:** One short link that randomly redirects to different destinations
4. **Geo-targeting:** Redirect to different URLs based on the visitor's country
5. **Browser extension:** One-click URL shortening from any webpage

## 27.3 Long-Term Vision

1. **Premium plans:** Offer paid tiers with advanced analytics, more API calls, and priority support
2. **Mobile app:** Native iOS and Android apps for link management
3. **Webhooks:** Notify external services when a link is clicked
4. **Machine learning:** Detect and block malicious/spam URLs
5. **Open-source release:** Package the project as an open-source self-hosted URL shortener


# 28. Comparison with Existing Solutions

| Feature | 2GOI | Bitly | TinyURL | Short.io |
|---------|------|-------|---------|----------|
| URL shortening | Yes | Yes | Yes | Yes |
| Custom aliases | Yes | Yes (paid) | Yes | Yes |
| Click analytics | Yes | Yes | No | Yes |
| QR codes | Yes | Yes (paid) | No | Yes |
| Link expiration | Yes | No | No | Yes |
| Google OAuth | Yes | Yes | No | Yes |
| Custom domain | No (future) | Yes (paid) | No | Yes |
| Open source | Yes | No | No | No |
| Free tier | Unlimited | 10 links/month | Unlimited | 1000 links |
| Self-hosted | Yes | No | No | No |
| Cost | 0 rupees/month | $29+/month | Free | $19+/month |

2GOI offers many of the same features as paid services, completely free. The main areas where commercial services have an advantage are custom domains, team collaboration, and enterprise features.


# 29. Conclusion

This project successfully demonstrates the design, development, and deployment of a production-grade URL shortener. The key achievements are:

1. **A working production application** accessible at https://2goi.in, serving real users
2. **Efficient Base62 encoding** that generates short codes with zero collisions
3. **Sub-5-millisecond redirects** using Redis cache-aside pattern
4. **Comprehensive click analytics** with country, browser, device, and daily trend analysis
5. **Modern authentication** supporting both email/password and Google OAuth
6. **Production deployment** with Docker, custom domain, SSL, and auto-deployment from GitHub
7. **Robust architecture** with graceful degradation, fault tolerance, and security best practices

The project covers a wide range of computer science and software engineering topics: system design, database design, caching strategies, encoding algorithms, authentication protocols, API design, frontend development, containerization, cloud deployment, DNS configuration, and SEO.

Through the challenges encountered and solved during development, we gained practical experience with real-world engineering problems: IPv6 compatibility, JWT algorithm differences, DNS propagation, OAuth configuration, email delivery, and corporate firewall issues.

The scalability analysis demonstrates understanding of how the system would evolve to handle millions of users, including horizontal scaling, database sharding, distributed caching, edge computing, and stream processing.

This project serves as both a functional product and a comprehensive demonstration of full-stack web development skills, suitable for academic evaluation and professional portfolio purposes.


# 30. References

1. Fielding, R. T. (2000). "Architectural Styles and the Design of Network-based Software Architectures." Doctoral dissertation, University of California, Irvine. (REST architecture)
2. Jones, M., Bradley, J., and Sakimura, N. (2015). "RFC 7519: JSON Web Token (JWT)." Internet Engineering Task Force.
3. FastAPI Documentation. https://fastapi.tiangolo.com/
4. React Documentation. https://react.dev/
5. Redis Documentation. https://redis.io/documentation
6. PostgreSQL Documentation. https://www.postgresql.org/docs/
7. Supabase Documentation. https://supabase.com/docs
8. Docker Documentation. https://docs.docker.com/
9. TailwindCSS Documentation. https://tailwindcss.com/docs
10. SQLAlchemy Documentation. https://docs.sqlalchemy.org/
11. Pydantic Documentation. https://docs.pydantic.dev/
12. Render Documentation. https://render.com/docs
13. Resend Documentation. https://resend.com/docs
14. Google Cloud OAuth Documentation. https://developers.google.com/identity/protocols/oauth2
15. Google Search Console Documentation. https://developers.google.com/search/docs
16. Vite Documentation. https://vitejs.dev/guide/
17. Recharts Documentation. https://recharts.org/
18. "Designing a URL Shortener." System Design Interview by Alex Xu.
19. "Base62 Encoding." Wikipedia. https://en.wikipedia.org/wiki/Base62
20. "Birthday Problem." Wikipedia. https://en.wikipedia.org/wiki/Birthday_problem


# Appendix A: Complete Code Walkthrough

## Backend File List

| File | Lines | Purpose |
|------|-------|---------|
| main.py | ~150 | Application entry point. Creates FastAPI app, registers routers, configures CORS, serves static files, handles SPA fallback |
| config.py | ~30 | Loads settings from environment variables using Pydantic BaseSettings |
| database.py | ~40 | Creates async SQLAlchemy engine with connection pooling and SSL |
| redis_client.py | ~25 | Creates async Redis client, handles connection failures gracefully |
| auth.py | ~80 | Verifies JWT tokens (ES256 via JWKS, HS256 fallback), auto-creates user records |
| middleware.py | ~20 | Rate limiting using SlowAPI (100/min anon, 1000/min auth) |
| models/link.py | ~30 | Link table: id, sequence_id, original_url, short_code, user_id, click_count, is_active, timestamps |
| models/click.py | ~25 | Click table: id, link_id, country, browser, device_type, referrer, ip_hash, clicked_at |
| models/daily_stats.py | ~20 | DailyClickStats table: id, link_id, date, click_count (with unique constraint) |
| models/user.py | ~15 | User table: id, email, plan, created_at |
| schemas/link.py | ~50 | Pydantic models: LinkCreate (input), ShortenResponse (output), LinkListResponse (list) |
| schemas/click.py | ~40 | Pydantic models: AnalyticsResponse, CountryBreakdown, DeviceBreakdown, BrowserBreakdown |
| services/shortener.py | ~120 | Base62 encoding, link creation (insert+flush+encode), QR generation, URL lookup, pagination |
| services/analytics.py | ~100 | Click logging (background task), daily upsert, analytics queries |
| routers/shorten.py | ~40 | POST /api/shorten endpoint |
| routers/redirect.py | ~60 | GET /{code} redirect endpoint with Redis cache check |
| routers/links.py | ~50 | GET /api/links and DELETE /api/links/{id} endpoints |
| routers/analytics.py | ~30 | GET /api/analytics/{code} endpoint |
| routers/health.py | ~30 | GET /api/health endpoint |

## Frontend File List

| File | Lines | Purpose |
|------|-------|---------|
| App.jsx | ~80 | Root component: routing setup, auth provider, navbar, toast notifications |
| main.jsx | ~10 | Entry point: renders App into the DOM |
| lib/supabase.js | ~10 | Supabase client initialization with URL and anon key |
| lib/api.js | ~60 | Axios HTTP client with JWT interceptor, API helper functions |
| context/AuthContext.jsx | ~100 | Authentication context: user state, signUp, signIn, signOut, signInWithGoogle |
| components/Navbar.jsx | ~70 | Navigation bar: dynamic based on auth state |
| components/ShortenForm.jsx | ~190 | URL input, advanced options (alias, expiry), result display with QR and copy |
| components/ProtectedRoute.jsx | ~30 | Auth guard: loading spinner, redirect to /login if not authenticated |
| pages/HomePage.jsx | ~120 | Landing page: hero, shortener form, feature cards, footer |
| pages/LoginPage.jsx | ~150 | Login form: email/password + Google OAuth |
| pages/SignupPage.jsx | ~170 | Signup form: email/password with confirmation + Google OAuth |
| pages/DashboardPage.jsx | ~230 | Links table with sort, copy, analytics, delete, pagination |
| pages/AnalyticsPage.jsx | ~240 | Analytics dashboard: line chart, bar chart, pie chart, browser bars |

## Infrastructure File List

| File | Purpose |
|------|---------|
| Dockerfile | Multi-stage build: Stage 1 builds React, Stage 2 sets up Python backend |
| render.yaml | Render Blueprint: web service (Docker) + Redis service with env vars |
| docker-compose.yml | Local development: backend + Redis |
| .gitignore | Excludes .env, node_modules, venv, build artifacts |
| frontend/index.html | SEO meta tags, Open Graph, Twitter cards, JSON-LD structured data |
| frontend/public/sitemap.xml | Lists all public pages for Google crawler |
| frontend/public/robots.txt | Allows crawlers, blocks /api/ |
| supabase/migrations/001_initial_schema.sql | Database schema (tables, indexes, sequences) |


# Appendix B: Environment Variables

## Backend Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | postgresql+asyncpg://user:pass@host:5432/db | Async PostgreSQL connection string |
| DATABASE_URL_SYNC | Yes | postgresql://user:pass@host:5432/db | Sync PostgreSQL connection string |
| SUPABASE_URL | Yes | https://xxx.supabase.co | Supabase project URL |
| SUPABASE_SERVICE_ROLE_KEY | Yes | eyJ... | Admin key (NEVER expose in frontend) |
| SUPABASE_ANON_KEY | Yes | eyJ... | Public key |
| SUPABASE_JWT_SECRET | Yes | your-secret | JWT secret for HS256 fallback |
| REDIS_URL | Yes | redis://host:6379 | Redis connection string |
| BASE_URL | Yes | https://2goi.in | Domain for short URLs |
| FRONTEND_URL | Yes | https://2goi.in | Same as BASE_URL |
| ENVIRONMENT | No | production | Controls logging and debug |
| RATE_LIMIT_ANON | No | 100 | Requests/min for anonymous users |
| RATE_LIMIT_AUTH | No | 1000 | Requests/min for authenticated users |
| CORS_ORIGINS | No | https://2goi.in | Allowed CORS origins |

## Frontend Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| VITE_API_URL | No | (empty) | Backend URL (empty = same domain) |
| VITE_SUPABASE_URL | Yes | https://xxx.supabase.co | Supabase project URL |
| VITE_SUPABASE_ANON_KEY | Yes | eyJ... | Supabase public key |


# Appendix C: Database Schema SQL

```sql
-- Create sequence for Base62 ID generation (starts at 10000 for 3+ char codes)
CREATE SEQUENCE IF NOT EXISTS links_sequence_id_seq START WITH 10000;

-- Users table (synced from Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Links table (shortened URLs)
CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id BIGINT UNIQUE NOT NULL DEFAULT nextval('links_sequence_id_seq'),
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    click_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Clicks table (raw click events)
CREATE TABLE IF NOT EXISTS clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    country VARCHAR(10),
    browser VARCHAR(50),
    device_type VARCHAR(20),
    referrer VARCHAR(2048),
    ip_hash VARCHAR(64),
    clicked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily click stats (pre-aggregated for fast analytics)
CREATE TABLE IF NOT EXISTS daily_click_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    click_count INTEGER DEFAULT 0,
    UNIQUE(link_id, date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_links_short_code ON links(short_code);
CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id);
CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id);
CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks(clicked_at);
CREATE INDEX IF NOT EXISTS idx_daily_stats_link_date ON daily_click_stats(link_id, date);
```


# Appendix D: API Documentation

Full interactive API documentation is available at: https://2goi.in/api/docs (Swagger UI)

| Method | Endpoint | Auth | Request Body | Response |
|--------|----------|------|-------------|----------|
| POST | /api/shorten | Optional | {"url": "...", "custom_alias": "...", "expires_in": 0} | {"short_url", "short_code", "original_url", "qr_code", "expires_at"} |
| GET | /{code} | No | — | 302 Redirect |
| GET | /api/links | Required | — | {"links": [...], "total", "page", "page_size"} |
| DELETE | /api/links/{id} | Required | — | 204 No Content |
| GET | /api/analytics/{code}?days=30 | Required | — | {"total_clicks", "countries", "devices", "browsers", "daily_clicks"} |
| GET | /api/health | No | — | {"status", "database", "redis"} |


# Appendix E: Glossary of Terms

| Term | Definition |
|------|-----------|
| API | Application Programming Interface — a set of rules for how software components communicate |
| ASGI | Asynchronous Server Gateway Interface — Python's async web server standard |
| Base62 | A number encoding using 62 characters (0-9, a-z, A-Z) |
| Cache | A high-speed data storage layer for frequently accessed data |
| CDN | Content Delivery Network — servers distributed worldwide to serve content faster |
| CI/CD | Continuous Integration/Continuous Deployment — automated build and deploy pipeline |
| CORS | Cross-Origin Resource Sharing — browser security mechanism for cross-domain requests |
| CSRF | Cross-Site Request Forgery — an attack that tricks users into making unwanted requests |
| DNS | Domain Name System — translates domain names (2goi.in) to IP addresses |
| Docker | A platform for building and running applications in isolated containers |
| ES256 | Elliptic Curve Digital Signature Algorithm with SHA-256 — an asymmetric signing algorithm |
| GDPR | General Data Protection Regulation — European privacy law |
| HS256 | HMAC with SHA-256 — a symmetric signing algorithm |
| HTTP 302 | Found — a redirect status code that tells the browser to go to a different URL |
| HTTP 410 | Gone — indicates the resource existed but has been permanently removed |
| JWT | JSON Web Token — a compact, URL-safe token format for transmitting claims |
| JWKS | JSON Web Key Set — a set of public keys for verifying JWT signatures |
| LRU | Least Recently Used — a cache eviction policy that removes the least recently accessed items |
| OAuth | Open Authorization — a protocol for delegating authentication to a third party (like Google) |
| ORM | Object-Relational Mapping — maps database tables to programming language objects |
| QR Code | Quick Response Code — a 2D barcode that encodes data (like a URL) |
| REST | Representational State Transfer — an architectural style for web APIs |
| SHA-256 | Secure Hash Algorithm 256-bit — a cryptographic hash function |
| SPA | Single-Page Application — a web app that loads a single HTML page and dynamically updates content |
| SQL | Structured Query Language — the standard language for interacting with relational databases |
| SSL/TLS | Secure Sockets Layer/Transport Layer Security — protocols for encrypted internet communication |
| TTL | Time To Live — the duration a cached item remains valid before being automatically deleted |
| URL | Uniform Resource Locator — a web address |
| UUID | Universally Unique Identifier — a 128-bit identifier that is unique across all systems |
| Upsert | A combination of UPDATE and INSERT — inserts if new, updates if exists |
| XSS | Cross-Site Scripting — an attack that injects malicious scripts into web pages |

---

---


# Appendix F: Interview Questions and Answers (Resume Preparation)

This section is specifically designed to help you confidently explain this project in interviews. Every question is answered in simple language with real examples from the project.

## F.1 General Project Questions

### Q: What is your project about? Explain in 2 lines.

**A:** 2GOI is a production-grade URL shortener deployed at https://2goi.in. It converts long URLs into short links like 2goi.in/2Bi, tracks every click with analytics (country, browser, device), and supports features like QR codes, custom aliases, link expiration, and Google login.

### Q: Why did you choose to build a URL shortener?

**A:** A URL shortener is one of the most popular system design interview questions at FAANG companies. It covers a wide range of engineering concepts: database design, caching, encoding algorithms, authentication, API design, and deployment. Building one end-to-end demonstrates full-stack proficiency and system design thinking.

### Q: What makes your project different from a basic URL shortener?

**A:** Most academic URL shortener projects just map a random string to a URL. My project goes further:
- Uses Base62 encoding from sequential IDs (zero collisions, same as Bitly)
- Redis caching for sub-5ms redirects (cache-aside pattern)
- Async click logging that never slows down redirects (BackgroundTasks)
- Pre-aggregated daily stats using PostgreSQL upsert (O(days) instead of O(clicks))
- Google OAuth + email authentication
- QR code generation for every link
- Actually deployed in production with custom domain, SSL, and CI/CD

### Q: Is this project deployed? Can I see it?

**A:** Yes, it is live at https://2goi.in. You can shorten a URL right now, click the short link, and see the redirect happen in milliseconds. If you create an account, you can see the analytics dashboard with charts.

### Q: How long did it take to build?

**A:** The core application (backend API, frontend, database) took about 2-3 weeks. Additional features like Google OAuth, Resend email integration, SEO setup, and comprehensive documentation took another 1-2 weeks. Total development time was approximately one month.

### Q: Did you build this alone or in a team?

**A:** I built this project individually, handling everything from system design and database schema to frontend UI, backend API, Docker deployment, DNS configuration, and documentation.

## F.2 Technical Architecture Questions

### Q: Explain the architecture of your project.

**A:** The project uses a single-domain architecture. Everything runs on one domain (2goi.in) in one Docker container:

- **Frontend:** React 19 SPA compiled to static files by Vite
- **Backend:** FastAPI (Python) with 4 Gunicorn/Uvicorn workers
- **Database:** PostgreSQL on Supabase (AWS Mumbai region)
- **Cache:** Redis on Render (25MB, LRU eviction)
- **Auth:** Supabase Auth (JWT tokens with ES256 signing)

The backend serves the compiled frontend as static files. API calls go to /api/* routes. Short URL redirects go to /{code}. All other paths serve index.html for client-side routing.

### Q: Why did you choose single-domain over separate frontend and backend?

**A:** Three reasons:
1. **No CORS issues** — Frontend and API are on the same origin, so browsers allow all requests without CORS configuration
2. **Short URLs work naturally** — 2goi.in/2Bi goes to the same server, no subdomain needed
3. **Simpler deployment** — One Docker container, one SSL certificate, one Render service

### Q: Why FastAPI instead of Django or Flask?

**A:** FastAPI has three key advantages for this project:
1. **Native async support** — Essential for concurrent Redis and database calls without blocking
2. **Automatic API documentation** — Swagger UI is generated automatically at /api/docs
3. **Pydantic integration** — Request/response validation is built into the framework with type hints

Django would be overkill (we don't need its admin panel or ORM — we use SQLAlchemy). Flask lacks native async support and automatic documentation.

### Q: Why PostgreSQL instead of MongoDB?

**A:** PostgreSQL is the right choice because:
1. **Relational data** — Links, clicks, and users have clear relationships (foreign keys)
2. **ACID transactions** — Critical for atomic click counting and upserts
3. **Sequences** — PostgreSQL SEQUENCE generates unique sequential IDs for Base62 encoding
4. **Upsert support** — INSERT ON CONFLICT is essential for our daily stats aggregation
5. **Free on Supabase** — 500MB free tier with connection pooling

MongoDB would be a poor fit because our data is inherently relational and we need transactions for accurate analytics.

### Q: Why Redis? Can't you just use the database?

**A:** We could, but redirects would be 5-10x slower. A database query takes 20-50ms due to network, query parsing, and disk I/O. Redis keeps data in RAM, so reads take 1-3ms. For the redirect endpoint, which is called on every click, this difference is massive.

Redis is also used for automatic link expiry (TTL). When a link expires, Redis deletes the cached entry automatically — no cleanup job needed.

However, Redis is optional in our design. If Redis goes down, redirects fall back to database queries. Slower, but still functional.

## F.3 Algorithm and Data Structure Questions

### Q: How does your URL shortening algorithm work?

**A:** We use Base62 encoding from sequential database IDs:

1. User submits a URL
2. We INSERT a row into PostgreSQL — the database generates a unique sequence_id (like 10008)
3. We convert 10008 to Base62: divide repeatedly by 62, map remainders to characters
4. 10008 → "2Bq" (the short code)
5. We UPDATE the row with this short code

Base62 uses 62 characters: 0-9, a-z, A-Z. With 6 characters, we can generate 56 billion unique codes.

### Q: Walk me through the Base62 encoding of the number 10000.

**A:**
```
Step 1: 10000 ÷ 62 = 161, remainder = 18 → character 'i'
Step 2: 161 ÷ 62 = 2, remainder = 37 → character 'B'  
Step 3: 2 ÷ 62 = 0, remainder = 2 → character '2'

Read remainders in reverse: "2Bi"
```

So 2goi.in/2Bi corresponds to the 10,000th link created.

### Q: Why Base62 instead of random strings?

**A:** Random strings have a collision problem. As the database grows, the chance of generating a code that already exists increases (birthday paradox). After 300,000 links, there is already a 1% collision chance. Each collision requires a retry (extra database query).

Base62 from sequential IDs has zero collisions because every integer maps to a unique string. No retries, no extra queries, O(1) performance forever. This is how Bitly and YouTube generate their IDs.

### Q: Why start the sequence at 10000 instead of 1?

**A:** Numbers 0-61 produce 1-character codes, and 62-3843 produce 2-character codes. These are too short and could conflict with URL routes. Starting at 10000 guarantees all codes are at least 3 characters, which looks professional and avoids routing conflicts.

### Q: How do you handle hash collisions?

**A:** We do not have hash collisions because we do not use hashing for code generation. We use deterministic Base62 encoding from sequential IDs. Every ID maps to exactly one unique code. This is a deliberate design choice to eliminate the collision problem entirely.

### Q: What data structures does Redis use internally for your cache?

**A:** Redis uses a hash table (dictionary) internally for its key-value store. Our keys are strings like "url:2Bq" and values are strings like "https://google.com". Redis hash tables provide O(1) average-case lookups, which is why Redis is so fast.

## F.4 Database Questions

### Q: Explain your database schema.

**A:** Four tables:

1. **links** — Core table. Fields: id (UUID PK), sequence_id (BIGINT, for Base62), original_url, short_code (UNIQUE), user_id (FK to users), click_count, is_active, created_at, expires_at
2. **clicks** — Raw click events. Fields: id, link_id (FK), country, browser, device_type, referrer, ip_hash, clicked_at
3. **daily_click_stats** — Pre-aggregated daily counts. Fields: id, link_id (FK), date, click_count. UNIQUE(link_id, date) enables upsert
4. **users** — User accounts. Fields: id (matches Supabase Auth UUID), email, plan, created_at

### Q: What is the upsert pattern and why do you use it?

**A:** Upsert means INSERT if the row does not exist, UPDATE if it does. We use it for the daily_click_stats table:

```sql
INSERT INTO daily_click_stats (link_id, date, click_count)
VALUES ('uuid', '2026-03-17', 1)
ON CONFLICT (link_id, date)
DO UPDATE SET click_count = daily_click_stats.click_count + 1;
```

First click of the day: creates a new row with click_count = 1.
Every subsequent click: increments click_count by 1.

This single SQL statement is atomic — safe under concurrent access. Without upsert, we would need a SELECT (to check if row exists), then either INSERT or UPDATE — requiring a transaction lock and two queries.

### Q: Why UUID for primary keys instead of auto-increment integers?

**A:** Security and distributed-system compatibility:
1. **Auto-increment leaks information.** If link ID is 5000, attackers know about 5000 links exist.
2. **UUIDs are globally unique.** They can be generated on any server without coordination — important for sharding.
3. **Safe to expose in APIs.** UUIDs in URLs reveal nothing about the database structure.

We still use a separate auto-increment sequence_id for Base62 encoding because UUIDs are too long for short codes.

### Q: What is the difference between soft delete and hard delete? Which do you use?

**A:** Hard delete removes the row from the database permanently. Soft delete sets a flag (is_active = false) to mark the row as deleted, but the data remains.

We use soft delete for links because:
1. **Analytics preservation** — Click history is retained even after the link is "deleted"
2. **Accidental deletion recovery** — The link can be reactivated
3. **Audit trail** — We know when links were created and deactivated

The redirect router checks `is_active = true` and returns 404 for soft-deleted links.

### Q: What indexes do you have and why?

**A:** Key indexes:
- **links.short_code** (UNIQUE) — Used on every redirect. Without this, every redirect would scan the entire links table. With the index, it is an O(log n) B-tree lookup.
- **links.user_id** — Used on the dashboard page to filter links by user.
- **clicks.link_id** — Used for analytics queries that filter clicks by link.
- **daily_click_stats(link_id, date)** (UNIQUE composite) — Enables the upsert pattern and fast daily trend queries.

### Q: How do you prevent race conditions in click counting?

**A:** Atomic SQL operations. Instead of:
```python
# BAD: Read-modify-write (race condition)
count = db.query(link.click_count)  # Thread A reads 5, Thread B reads 5
link.click_count = count + 1        # Both set to 6, should be 7
db.commit()
```

We use:
```sql
-- GOOD: Atomic increment (no race condition)
UPDATE links SET click_count = click_count + 1 WHERE id = :link_id
```

PostgreSQL executes this atomically. Even with 100 concurrent clicks, every increment is counted correctly.

## F.5 Caching Questions

### Q: Explain your caching strategy.

**A:** We use the cache-aside (lazy loading) pattern with Redis:

1. Redirect request comes in for short code "2Bq"
2. Check Redis: GET "url:2Bq"
3. If found (cache hit): return the URL immediately (3-5ms)
4. If not found (cache miss): query PostgreSQL, store result in Redis, return the URL (20-50ms, but next request will be a cache hit)

We also proactively cache URLs when links are created, so the first click is usually a cache hit.

### Q: What happens when Redis is down?

**A:** The application continues working. Every Redis operation is wrapped in try-except. If Redis fails, we skip the cache and query the database directly. Redirects are slower (20-50ms instead of 3-5ms) but still functional.

This is a deliberate design decision: Redis is a performance optimization, not a requirement. The database is the source of truth.

### Q: What is LRU eviction?

**A:** LRU stands for Least Recently Used. When Redis runs out of memory (25MB on free tier), it needs to remove some keys to make space. LRU removes the keys that have not been accessed for the longest time.

This is ideal for our use case: popular links (frequently clicked) stay in cache, while rarely-clicked links are evicted. If an evicted link is clicked again, it causes a cache miss, the URL is fetched from the database, and it re-enters the cache.

### Q: How many URLs can you cache in 25MB?

**A:** Approximately 170,000 URLs. Average URL is about 100 bytes, key overhead is about 50 bytes, so each entry is roughly 150 bytes. 25MB / 150 bytes = approximately 170,000 entries.

## F.6 Authentication Questions

### Q: How does JWT authentication work in your project?

**A:** 
1. User logs in via Supabase (email/password or Google OAuth)
2. Supabase issues a JWT token signed with ES256 algorithm
3. Frontend stores the token (Supabase JS client manages this in localStorage)
4. On every API call, our Axios interceptor attaches the token: `Authorization: Bearer eyJ...`
5. Backend extracts the token, fetches Supabase's public keys from JWKS endpoint
6. Verifies the signature using the public key (ES256)
7. Extracts user_id from the "sub" claim
8. Looks up or creates the user record in our database

### Q: What is the difference between ES256 and HS256?

**A:**
- **HS256 (symmetric):** Same secret key is used to sign and verify. Both the issuer (Supabase) and verifier (our backend) must know the secret. If the secret leaks, anyone can forge tokens.
- **ES256 (asymmetric):** A private key signs the token, a public key verifies it. Only Supabase has the private key. Our backend only needs the public key, which is safe to share. If the public key is exposed, no one can forge tokens because they do not have the private key.

Supabase uses ES256 by default. We fetch the public key from their JWKS endpoint.

### Q: What is JWKS?

**A:** JWKS stands for JSON Web Key Set. It is a standard protocol where the authentication provider publishes its public keys at a well-known URL. Our backend fetches keys from `https://xxx.supabase.co/auth/v1/.well-known/jwks.json`. 

The advantage: if Supabase rotates its signing keys (for security), our backend automatically uses the new keys. No code changes or redeployment needed.

### Q: How does Google OAuth work in your project?

**A:**
1. User clicks "Continue with Google"
2. Browser redirects to Google's login page
3. User enters Google credentials
4. Google asks for permission (email + profile)
5. Google redirects to Supabase's callback URL with an authorization code
6. Supabase exchanges the code for the user's Google profile
7. Supabase creates/updates the user account and issues a JWT
8. Browser redirects to our app with the token
9. User is now logged in

Key point: We never see the user's Google password. Google handles all password verification.

### Q: What is the difference between authentication and authorization?

**A:**
- **Authentication:** Verifying WHO the user is (login with email/password or Google)
- **Authorization:** Verifying WHAT the user can do (can this user view this link's analytics? can they delete this link?)

In our project, authentication is handled by Supabase (issuing JWT tokens). Authorization is handled by our backend (checking if the user_id in the token matches the link's user_id before allowing analytics access or deletion).

## F.7 Performance and Scalability Questions

### Q: What is the response time for a redirect?

**A:** 3-5ms for a cache hit (Redis), 20-50ms for a cache miss (database). The click logging happens asynchronously in a background task, so it adds zero latency to the redirect response.

### Q: How would you handle 1 million requests per second?

**A:** Current setup handles hundreds of requests/second. For millions, we would need:

1. **Horizontal scaling:** Multiple identical servers behind a load balancer
2. **Redis Cluster:** Distributed cache across multiple nodes
3. **Read replicas:** PostgreSQL replicas for read-heavy redirect traffic
4. **Database sharding:** Split data across multiple DB instances by short code prefix
5. **CDN/Edge caching:** Deploy Redis caches at global edge locations
6. **L1 in-process cache:** Hot links cached in application memory (no network call)

### Q: What is the birthday paradox and how does it relate to URL shorteners?

**A:** The birthday paradox says that in a group of 23 people, there is a 50% chance that two share the same birthday. This is counterintuitive because there are 365 possible birthdays.

For URL shorteners using random codes: with 62^6 = 56 billion possible codes, you might think collisions are unlikely. But due to the birthday paradox, after just 300,000 links, collision probability is 1%. After 7.5 million links, it is 50%.

This is why we use sequential Base62 encoding instead of random strings — zero collision probability, ever.

### Q: How does your pre-aggregation improve analytics performance?

**A:** Without pre-aggregation, getting "clicks per day for 30 days" scans ALL click rows:
```
Link with 1,000,000 clicks → scan 1,000,000 rows → slow
```

With pre-aggregation (daily_click_stats table), we read exactly 30 rows:
```
30 days of data → read 30 rows → fast, regardless of total clicks
```

This is a 33,000x improvement for a link with 1 million clicks. The pre-aggregation happens on every click via the upsert pattern, so it adds minimal overhead to writes.

## F.8 Deployment and DevOps Questions

### Q: How is your application deployed?

**A:** Docker multi-stage build deployed on Render:

- **Stage 1:** Node.js 20 builds the React frontend (npm ci + npm run build)
- **Stage 2:** Python 3.11 slim image, copies backend code + built frontend, installs pip dependencies

Render reads our render.yaml Blueprint to create a web service (Docker) and Redis service. Auto-deploy triggers on every git push to master.

### Q: What is a multi-stage Docker build and why use it?

**A:** A multi-stage build uses multiple FROM statements. Each stage can use a different base image. Only the final stage becomes the deployed image.

We use it because the frontend needs Node.js to build, but the production image only needs Python. Without multi-stage, the image would include both runtimes (1GB+). With multi-stage, the final image is only ~300MB because Node.js is discarded after the build.

### Q: How does CI/CD work in your project?

**A:**
1. I push code to GitHub (master branch)
2. Render detects the push via webhook
3. Render builds a new Docker image from the Dockerfile
4. Render deploys the new container
5. Render pings /api/health to verify the deployment
6. If healthy, traffic switches to the new container
7. If unhealthy, Render keeps the old container running

The entire process takes 3-5 minutes and requires zero manual intervention.

### Q: What is the health check endpoint?

**A:** GET /api/health returns:
```json
{"status": "healthy", "database": "connected", "redis": "connected"}
```

It pings both PostgreSQL and Redis. Render calls this every few minutes. If it fails repeatedly, Render restarts the service. This is critical for production reliability.

## F.9 Security Questions

### Q: How do you prevent SQL injection?

**A:** We use SQLAlchemy ORM, which automatically parameterizes all queries. User input is never concatenated into SQL strings. For example:

```python
# SQLAlchemy generates: SELECT * FROM links WHERE short_code = $1 (parameterized)
result = await db.execute(select(Link).where(Link.short_code == user_input))
```

Even if user_input is `"'; DROP TABLE links; --"`, it is treated as a string value, not SQL code.

### Q: How do you handle user privacy?

**A:** We never store raw IP addresses. Every IP is hashed with SHA-256 before storage:
```python
ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
```
The hash is one-way — we cannot recover the original IP from the hash. But the same IP always produces the same hash, so we can still count unique visitors.

### Q: How do you prevent abuse?

**A:** Rate limiting using SlowAPI:
- Anonymous users: 100 API requests per minute
- Authenticated users: 1000 API requests per minute
- Exceeding the limit returns HTTP 429 (Too Many Requests)

This prevents database spam (mass link creation), brute-force attacks, and denial-of-service attempts.

## F.10 Basic Concept Questions (Fundamentals)

### Q: What is an API?

**A:** API stands for Application Programming Interface. It is a set of rules that allows different software systems to communicate. In our project, the frontend (React) communicates with the backend (FastAPI) through a REST API. The frontend sends HTTP requests (like POST /api/shorten), and the backend returns JSON responses.

### Q: What is REST?

**A:** REST (Representational State Transfer) is an architectural style for web APIs. Key principles:
- Resources are identified by URLs (/api/links, /api/analytics)
- HTTP methods define actions (GET = read, POST = create, DELETE = remove)
- Responses are typically JSON
- Each request is stateless (contains all needed information)

### Q: What is a JWT?

**A:** JWT (JSON Web Token) is a compact, URL-safe token format. It has three parts: Header (algorithm info), Payload (user data like user_id and email), and Signature (proves the token was not tampered with). JWTs are used for stateless authentication — the server does not need to store session data.

### Q: What is OAuth?

**A:** OAuth (Open Authorization) is a protocol that lets users log in to your app using an existing account (like Google). The key idea: the user enters their password on Google's site, not yours. Google verifies the password and tells your app "yes, this user is legitimate." You never see the user's Google password.

### Q: What is Docker?

**A:** Docker packages an application and all its dependencies into a "container" — a lightweight, portable unit that runs the same way everywhere. Our Dockerfile defines exactly how to build and run 2GOI. Whether running on a developer's laptop or Render's cloud servers, the container behaves identically.

### Q: What is a database index?

**A:** An index is a data structure (usually a B-tree) that speeds up database lookups. Without an index on short_code, finding a link requires scanning every row in the table (O(n)). With an index, it is a tree traversal (O(log n)). For a table with 1 million rows, that is the difference between checking 1,000,000 rows and checking about 20 levels.

### Q: What is connection pooling?

**A:** Opening a database connection takes 50-100ms (TCP handshake, SSL, authentication). If we opened a new connection for every request, this overhead adds up. Connection pooling keeps a pool of pre-established connections. Requests borrow a connection from the pool (instant) and return it when done. Our pool keeps 5 connections ready and can grow to 15 under load.

### Q: What is async/await?

**A:** Async/await lets a program do other work while waiting for slow operations (like database queries or Redis calls). In a synchronous program, if Worker A is waiting for a database query, it is blocked and cannot do anything else. With async, Worker A starts the query, yields control, handles other requests, and resumes when the query completes. This dramatically increases throughput.

### Q: What is CORS?

**A:** CORS (Cross-Origin Resource Sharing) is a browser security mechanism. It prevents JavaScript on one domain from making requests to another domain. For example, JavaScript on evil.com cannot call our API at 2goi.in unless we explicitly allow it. Our single-domain architecture avoids CORS issues entirely because the frontend and API are on the same origin.

### Q: What is HTTP 302?

**A:** HTTP 302 is the "Found" redirect status code. When our server receives a request for 2goi.in/2Bi, it responds with status 302 and a Location header pointing to the original URL. The browser automatically follows the redirect and loads the original page. We chose 302 (temporary redirect) over 301 (permanent redirect) because the link might be updated or expired in the future.

### Q: What is a CDN?

**A:** CDN (Content Delivery Network) is a global network of servers that caches content close to users. If our server is in Mumbai and a user in New York clicks a link, the request travels across the ocean (200-300ms). With a CDN, the redirect can be served from a server in Virginia (5ms). We do not currently use a CDN, but it would be the first scaling step for global users.


# Appendix G: Resume Bullet Points

Use these bullet points on your resume to describe this project. Each point highlights a specific technical achievement.

## Project Description (2-3 lines for resume)
**2GOI URL Shortener** — Full-stack URL shortening service with click analytics, deployed at https://2goi.in. Built with React 19, FastAPI, PostgreSQL, Redis, Docker, and Google OAuth. Implements Base62 encoding, cache-aside pattern, async analytics, and CI/CD.

## Individual Bullet Points (pick 5-8 for resume)

- Designed and deployed a production URL shortener serving real users at https://2goi.in with custom domain, SSL, and Docker-based CI/CD on Render
- Implemented collision-free Base62 encoding from sequential PostgreSQL IDs, supporting 56 billion+ unique short codes without duplicate checking
- Built Redis cache-aside pattern achieving sub-5ms redirect response times, with graceful degradation to database fallback on cache failure
- Developed async click analytics engine using FastAPI BackgroundTasks, logging country, browser, and device data without adding latency to redirects
- Optimized analytics queries 33,000x using PostgreSQL upsert (INSERT ON CONFLICT) for pre-aggregated daily click statistics
- Integrated Supabase Auth with ES256 JWT verification via JWKS endpoint, supporting email/password and Google OAuth authentication
- Built responsive React 19 SPA with TailwindCSS featuring real-time analytics charts (Recharts), QR code generation, and dark theme UI
- Containerized application using multi-stage Docker build (Node.js build + Python runtime), reducing image size by 60%
- Configured GoDaddy DNS, Resend SMTP (custom domain emails), and Google Search Console for production-ready deployment with SEO optimization
- Implemented rate limiting (SlowAPI), input validation (Pydantic), atomic click counting, and IP hashing for security and data integrity


# Appendix H: Real Code from the Repository

This appendix contains actual code from the project with line-by-line explanations.

## H.1 Base62 Encoding (backend/app/services/shortener.py)

```python
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    """Convert a positive integer to a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]       # Special case: 0 → "0"
    base = len(BASE62_ALPHABET)          # base = 62
    encoded = []
    while num:
        num, rem = divmod(num, base)     # divmod(10000, 62) → (161, 18)
        encoded.append(BASE62_ALPHABET[rem])  # ALPHABET[18] = 'i'
    return ''.join(reversed(encoded))    # Reverse: ['i','B','2'] → "2Bi"
```

**Why this works:** divmod(a, b) returns (quotient, remainder). The remainder maps to a character. We keep dividing until the quotient is 0. The characters are collected in reverse order (least significant digit first), so we reverse at the end.

## H.2 Link Creation with Two-Step Process (backend/app/services/shortener.py)

```python
async def create_short_link(db, original_url, custom_alias=None, expires_in=None, user_id=None):
    # Step 1: Check if custom alias is already taken
    if custom_alias:
        existing = await db.execute(select(Link).where(Link.short_code == custom_alias))
        if existing.scalar_one_or_none():
            raise ValueError(f"Custom alias '{custom_alias}' is already taken")

    # Step 2: Insert with temporary placeholder
    link = Link(
        original_url=original_url,
        short_code=custom_alias or "__pending__",  # Temporary until we get sequence_id
        user_id=user_id,
    )
    db.add(link)
    await db.flush()  # Flush triggers PostgreSQL to generate sequence_id

    # Step 3: Generate Base62 code from sequence_id
    if not custom_alias:
        link.short_code = encode_base62(link.sequence_id)  # 10008 → "2Bq"

    await db.commit()
    await db.refresh(link)
    return link
```

**Why two steps?** PostgreSQL generates the sequence_id only after the INSERT (or flush). We need the sequence_id to compute the Base62 code. So we insert first, get the ID, compute the code, and then update the record.

## H.3 Redirect with Redis Cache (backend/app/routers/redirect.py)

```python
@router.get("/{short_code}")
async def redirect_short_url(short_code, request, background_tasks, db):
    # Skip frontend routes
    frontend_routes = {"login", "signup", "dashboard", "analytics"}
    if short_code.startswith("api") or short_code in frontend_routes:
        raise HTTPException(status_code=404)

    # Step 1: Check Redis cache (fastest path)
    redis = await get_redis()
    try:
        cached_url = await redis.get(f"url:{short_code}")
    except Exception:
        cached_url = None

    if cached_url:
        # Cache HIT — redirect immediately, log click in background
        link = await get_link_by_code(db, short_code)
        if link:
            background_tasks.add_task(_log_click_background, link.id, ...)
        return RedirectResponse(url=cached_url, status_code=302)

    # Step 2: Cache MISS — query database
    link = await get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404)

    # Check expiration
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This link has expired")

    # Store in Redis for next time
    try:
        if link.expires_at:
            ttl = int((link.expires_at - datetime.utcnow()).total_seconds())
            await redis.setex(f"url:{short_code}", ttl, link.original_url)
        else:
            await redis.set(f"url:{short_code}", link.original_url)
    except Exception:
        pass  # Redis failure should not break redirect

    # Log click in background (does not block the redirect)
    background_tasks.add_task(_log_click_background, link.id, ...)
    return RedirectResponse(url=link.original_url, status_code=302)
```

**Key design decisions in this code:**
1. Frontend routes are explicitly skipped to avoid routing conflicts
2. Redis failure is caught silently (redirect still works via database)
3. Background tasks log clicks AFTER the response is sent
4. Expired links return HTTP 410 (Gone), not 404 (Not Found)
5. Cache is primed on miss so the next request is fast

## H.4 JWT Token Verification (backend/app/auth.py)

```python
# JWKS client fetches Supabase's public keys automatically
_jwks_client = PyJWKClient(f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json")

async def verify_token(token: str) -> dict:
    """Verify a Supabase JWT token. Tries ES256 first, falls back to HS256."""
    try:
        # Primary: ES256 verification via JWKS (modern tokens)
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = pyjwt.decode(token, signing_key.key, algorithms=["ES256"], audience="authenticated")
        return payload
    except Exception:
        pass

    # Fallback: HS256 verification with shared secret (legacy tokens)
    try:
        payload = pyjwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        return payload
    except pyjwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

**Why two verification methods?** Supabase primarily uses ES256 (asymmetric), but some edge cases produce HS256 tokens. The dual approach ensures compatibility with both. ES256 is tried first because it is more secure.

## H.5 Daily Click Stats Upsert (backend/app/services/analytics.py)

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Inside the log_click function:
today = date.today()
stmt = pg_insert(DailyClickStats).values(
    link_id=link_id, date=today, click_count=1
)
stmt = stmt.on_conflict_do_update(
    constraint="uq_daily_stats_link_date",  # The UNIQUE(link_id, date) constraint
    set_={"click_count": DailyClickStats.click_count + 1},
)
await db.execute(stmt)
```

**This is the most elegant SQL in the project.** One statement handles both "first click of the day" (INSERT) and "Nth click of the day" (UPDATE). It is atomic, concurrent-safe, and requires no application-level locking.

## H.6 Frontend Auth Context (frontend/src/context/AuthContext.jsx)

```javascript
// Supabase client handles all token management
const signIn = async (email, password) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
}

const signInWithGoogle = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/dashboard` }
    })
    if (error) throw error
}

// Axios interceptor attaches JWT to every API call
api.interceptors.request.use(async (config) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session) {
        config.headers.Authorization = `Bearer ${session.access_token}`
    }
    return config
})
```

**How this works:** The Supabase JS client manages tokens in localStorage. Our Axios interceptor reads the current session and attaches the JWT to every API request. The backend verifies this token on every protected endpoint.


# Appendix I: How to Explain This Project in an Interview (Script)

## 30-Second Elevator Pitch

"I built a production URL shortener called 2GOI, deployed at 2goi.in. It uses Base62 encoding for collision-free short codes, Redis caching for sub-5ms redirects, and async click analytics. The stack is React, FastAPI, PostgreSQL, Redis, and Docker. It supports Google login, QR codes, custom aliases, and link expiration. It is live in production with auto-deployment from GitHub."

## 2-Minute Detailed Explanation

"My project is 2GOI, a URL shortener like Bitly. You paste a long URL, and it gives you a short link like 2goi.in/2Bi.

The architecture is a single Docker container running on Render. React frontend is compiled by Vite and served as static files by a FastAPI backend. PostgreSQL on Supabase stores the data. Redis caches the most-clicked URLs for fast redirects.

The short codes are generated using Base62 encoding from sequential database IDs. This is the same approach Bitly and YouTube use. It guarantees zero collisions, unlike random string generation which suffers from the birthday paradox.

When someone clicks a short link, the system checks Redis first. If it is a cache hit, the redirect happens in under 5 milliseconds. If it is a cache miss, we query the database and cache the result. Click logging happens asynchronously in a background task, so it never slows down the redirect.

For analytics, I built a pre-aggregated daily stats table using PostgreSQL's upsert pattern. This means getting daily click trends reads 30 rows instead of scanning millions. Authentication uses Supabase with ES256 JWT verification via JWKS, supporting both email/password and Google OAuth.

The entire thing runs on free tiers — the only cost is the domain at about 67 rupees per month. It is live at 2goi.in right now."

## Handling Follow-Up Questions

**If they ask "What was the hardest part?"**
"The hardest challenge was JWT verification. Supabase uses ES256 (asymmetric) signing, but most tutorials only show HS256 (symmetric). I had to implement JWKS-based verification to fetch Supabase's public keys and verify the token signatures correctly. I also had to handle IPv6-only database connections by switching to Supabase's Session Pooler."

**If they ask "What would you do differently?"**
"I would add automated testing from the start — unit tests for the Base62 encoder and API integration tests. I would also implement a more sophisticated rate limiter that tracks by user account, not just IP address. For scale, I would consider a message queue like Kafka for click processing."

**If they ask "How would you scale this to millions of users?"**
"Horizontal scaling with a load balancer, Redis Cluster for distributed caching, PostgreSQL read replicas for redirect queries, database sharding by short code prefix for writes, and CDN edge caching for global latency reduction. I have documented all of this in the scalability section of my project report."


# Appendix J: Complete Project Folder Structure

```
windsurf-project/
│
├── frontend/                         # React 19 SPA (Single Page Application)
│   ├── index.html                    # Main HTML file with SEO meta tags, Open Graph, JSON-LD
│   ├── package.json                  # npm dependencies (react, react-router, recharts, tailwindcss)
│   ├── vite.config.js                # Vite build configuration (dev server, production build)
│   ├── tailwind.config.js            # TailwindCSS theme configuration
│   ├── postcss.config.js             # PostCSS plugins for TailwindCSS
│   ├── public/
│   │   ├── robots.txt                # Tells search engines what to crawl
│   │   ├── sitemap.xml               # Lists all public pages for Google
│   │   └── google9b5...html          # Google Search Console verification file
│   └── src/
│       ├── main.jsx                  # Entry point — renders <App/> into the DOM
│       ├── App.jsx                   # Root component — React Router + AuthProvider + Toaster
│       ├── index.css                 # Global styles + TailwindCSS imports
│       ├── lib/
│       │   ├── supabase.js           # Supabase client (URL + anon key)
│       │   └── api.js                # Axios instance with JWT interceptor + API helpers
│       ├── context/
│       │   └── AuthContext.jsx        # Auth state (user, signIn, signUp, signOut, Google OAuth)
│       ├── components/
│       │   ├── Navbar.jsx            # Top navigation bar (dynamic based on login state)
│       │   ├── ShortenForm.jsx       # URL input + advanced options + result display + QR code
│       │   └── ProtectedRoute.jsx    # Auth guard — redirects to /login if not authenticated
│       └── pages/
│           ├── HomePage.jsx          # Landing page — hero section + shortener form + feature cards
│           ├── LoginPage.jsx         # Email/password login + Google OAuth + error handling
│           ├── SignupPage.jsx        # Email/password signup + Google OAuth + confirmation message
│           ├── DashboardPage.jsx     # User's links table — sort, copy, delete, analytics, pagination
│           └── AnalyticsPage.jsx     # Charts — line chart (daily), bar chart (countries), pie (devices)
│
├── backend/                          # FastAPI Python backend
│   ├── requirements.txt              # Python dependencies (fastapi, sqlalchemy, redis, pyjwt, etc.)
│   ├── .env.example                  # Template for environment variables
│   └── app/
│       ├── main.py                   # App entry point — lifespan, CORS, routers, static files, SPA fallback
│       ├── config.py                 # Pydantic Settings — loads from env vars / .env file
│       ├── database.py               # Async SQLAlchemy engine + session factory + connection pool
│       ├── redis_client.py           # Async Redis client — cache-aside for redirects
│       ├── auth.py                   # JWT verification (ES256 JWKS + HS256 fallback) + user lookup
│       ├── middleware.py             # Rate limiting (SlowAPI — 100/min anon, 1000/min auth)
│       ├── models/
│       │   ├── link.py               # Link table — UUID PK, sequence_id, short_code, original_url
│       │   ├── click.py              # Click table — link_id, country, browser, device, ip_hash
│       │   ├── daily_stats.py        # DailyClickStats — pre-aggregated (link_id, date, count)
│       │   └── user.py               # User table — id (from Supabase), email, plan
│       ├── schemas/
│       │   ├── link.py               # Pydantic models — LinkCreate (input), ShortenResponse (output)
│       │   └── click.py              # Pydantic models — AnalyticsResponse, CountryBreakdown
│       ├── services/
│       │   ├── shortener.py          # Core logic — Base62 encode, create link, QR code, pagination
│       │   └── analytics.py          # Click logging (async), daily upsert, analytics queries
│       └── routers/
│           ├── shorten.py            # POST /api/shorten — create short link + prime cache
│           ├── redirect.py           # GET /{code} — Redis check → DB fallback → 302 redirect
│           ├── links.py              # GET /api/links + DELETE /api/links/{id} — dashboard data
│           ├── analytics.py          # GET /api/analytics/{code} — charts data
│           └── health.py             # GET /api/health — DB + Redis connectivity check
│
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql    # Database schema — tables, indexes, sequences, constraints
│
├── Dockerfile                        # Multi-stage build — Stage 1: Node.js (React), Stage 2: Python (FastAPI)
├── docker-compose.yml                # Local development — backend + Redis containers
├── render.yaml                       # Render Blueprint — web service (Docker) + Redis service
├── .gitignore                        # Ignored files — .env, node_modules, venv, build artifacts
├── README.md                         # Project overview — architecture, API, deployment
├── DOCUMENTATION.md                  # Detailed technical documentation
├── SETUP_GUIDE.md                    # Step-by-step setup for all external services
└── PROJECT_REPORT.md                 # This file — academic project report (NOT pushed to GitHub)
```


# Appendix K: Design Patterns Used in This Project

## K.1 Cache-Aside Pattern (Lazy Loading)

**What it is:** The application checks the cache before the database. If data is in cache, return it. If not, fetch from database, store in cache, then return.

**Where we use it:** The redirect router (`redirect.py`)

**Step-by-step:**
1. User visits `2goi.in/2Bi`
2. Code checks Redis: `GET url:2Bi`
3. **If Redis has it (cache hit):** Return the URL instantly (3ms)
4. **If Redis does not have it (cache miss):** Query PostgreSQL, store result in Redis, return the URL (30ms, but next click is 3ms)

**Why this pattern:**
- Most links are clicked many times → high cache hit rate
- Cache is optional → if Redis dies, app still works
- No stale data risk → URLs don't change after creation

## K.2 Write-Through Cache (Cache Priming)

**What it is:** When data is created, immediately write it to both the database AND the cache.

**Where we use it:** The shorten router (`shorten.py`)

**Step-by-step:**
1. User creates a short link
2. Link is saved to PostgreSQL
3. Link is immediately written to Redis: `SET url:2Bi https://google.com`
4. First click on this new link is already a cache hit

**Why this pattern:**
- New links are often clicked immediately after creation (user tests it)
- Eliminates the "cold start" problem for new links

## K.3 Cache Invalidation on Delete

**What it is:** When data is deleted, remove it from the cache too.

**Where we use it:** The links router (`links.py`) delete endpoint

**Step-by-step:**
1. User deletes a link from the dashboard
2. Link is soft-deleted in PostgreSQL (`is_active = false`)
3. Cache entry is removed: `DEL url:2Bi`
4. Next click returns 404 (not a stale redirect)

**Why this pattern:**
- Without invalidation, deleted links would still redirect until the cache entry expires
- Users expect immediate effect when they delete something

## K.4 Dependency Injection

**What it is:** Instead of creating objects inside a function, they are "injected" as parameters. FastAPI does this with `Depends()`.

**Where we use it:** Every router endpoint

**Example:**
```python
@router.get("/api/links")
async def list_links(
    db: AsyncSession = Depends(get_db),           # Database session injected
    current_user: User = Depends(require_auth),    # Authenticated user injected
):
    # We just use db and current_user — we don't create them ourselves
    links = await get_user_links(db, current_user.id)
```

**Why this pattern:**
- **Testable:** In tests, we can inject a mock database instead of a real one
- **Clean:** Router functions don't know how to create database connections
- **Automatic cleanup:** FastAPI closes the session when the request ends

## K.5 Background Task Pattern

**What it is:** Heavy work runs AFTER the response is sent to the user. The user does not wait.

**Where we use it:** Click logging in the redirect router

**Step-by-step:**
1. User clicks `2goi.in/2Bi`
2. Server finds the URL in Redis or database
3. Server sends 302 redirect IMMEDIATELY (3-30ms)
4. AFTER the response is sent, background task runs:
   - Parse User-Agent → get browser and device type
   - Hash IP address → SHA-256 for privacy
   - INSERT into clicks table
   - UPSERT into daily_click_stats table
   - INCREMENT click_count on links table

**Why this pattern:**
- Click logging takes 20-50ms (database writes)
- Without background tasks, the user waits 20-50ms extra for every click
- With background tasks, the user is already on the target page while we log the click

## K.6 Application Lifespan (Startup/Shutdown)

**What it is:** Code that runs once when the server starts and once when it stops.

**Where we use it:** `main.py` lifespan function

**On startup:**
- Create database tables if they don't exist (`Base.metadata.create_all`)
- Check if frontend static files exist
- Print status messages

**On shutdown:**
- Close Redis connection gracefully
- Dispose database engine (close all pooled connections)

**Why this pattern:**
- Tables should exist before the first request arrives
- Connections should be cleaned up when the server stops (avoids resource leaks)

## K.7 SPA Fallback (404 Handler)

**What it is:** When the server receives a request for a URL it doesn't recognize (like `/login` or `/dashboard`), it serves `index.html` instead of returning a 404 error.

**Where we use it:** `main.py` exception handler

**Step-by-step:**
1. User navigates to `2goi.in/dashboard`
2. FastAPI has no route for `/dashboard`
3. The 404 handler catches it
4. It checks: is this an API path? (`/api/*`) → No
5. It serves `index.html`
6. React Router inside `index.html` sees `/dashboard` and renders the Dashboard page

**Why this pattern:**
- React Router handles navigation on the client side
- Without this, refreshing the page on `/dashboard` would show a 404 error
- API routes (`/api/*`) still return proper 404 JSON responses

## K.8 Singleton Settings with @lru_cache

**What it is:** Configuration is loaded once and reused for all requests.

**Where we use it:** `config.py`

```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # Reads .env file only on first call
```

**Why this pattern:**
- Reading the `.env` file on every request would be slow
- `@lru_cache` ensures the Settings object is created once and cached forever
- All calls to `get_settings()` return the same object


# Appendix L: Step-by-Step Feature Walkthroughs

## L.1 Complete Walkthrough: Shortening a URL

This walkthrough follows a URL from the moment the user pastes it to the moment they receive the short link.

**Step 1: User Action**
- User opens `https://2goi.in`
- Types `https://www.example.com/very/long/path?param=value` into the input box
- Clicks "Shorten"

**Step 2: Frontend (ShortenForm.jsx)**
- `handleSubmit()` is called
- Sets `loading = true` (shows spinner on button)
- Calls `shortenUrl()` from `api.js`

**Step 3: API Call (api.js)**
- Axios interceptor checks if user is logged in
- If logged in: attaches JWT token as `Authorization: Bearer eyJ...`
- If anonymous: no token attached
- Sends: `POST /api/shorten` with body `{"url": "https://www.example.com/very/long/path?param=value"}`

**Step 4: Pydantic Validation (schemas/link.py)**
- FastAPI automatically validates the request body against `LinkCreate` schema
- Checks: is `url` a valid HTTP/HTTPS URL?
- If invalid: returns `422 Unprocessable Entity` immediately

**Step 5: Authentication Check (auth.py)**
- `get_current_user()` dependency is called
- If token present: verify with ES256/HS256, extract user_id, find or create User record
- If no token: returns `None` (anonymous user)

**Step 6: Link Creation (services/shortener.py)**
- `create_short_link()` is called
- Creates a Link object with `short_code = "__pending__"`
- `db.add(link)` → adds to session
- `await db.flush()` → PostgreSQL generates `sequence_id = 10008`
- `encode_base62(10008)` → returns `"2Bq"`
- Updates `link.short_code = "2Bq"`
- `await db.commit()` → saves to database

**Step 7: Cache Priming (routers/shorten.py)**
- `redis.set("url:2Bq", "https://www.example.com/very/long/path?param=value")` → stored in Redis
- If Redis is down → caught by try/except, link creation still succeeds

**Step 8: QR Code Generation (services/shortener.py)**
- `generate_qr_code("https://2goi.in/2Bq")` → creates QR code image
- Rendered as PNG → encoded as Base64 string
- Result: `"iVBORw0KGg..."` (long Base64 string)

**Step 9: Response**
- Server returns:
```json
{
    "short_url": "https://2goi.in/2Bq",
    "short_code": "2Bq",
    "original_url": "https://www.example.com/very/long/path?param=value",
    "qr_code": "iVBORw0KGg...",
    "expires_at": null
}
```

**Step 10: Frontend Display**
- `ShortenForm.jsx` receives the response
- Shows the short URL as a clickable link
- Shows copy button (uses `navigator.clipboard.writeText`)
- Shows QR code image (using `<img src="data:image/png;base64,{qr_code}">`)
- Shows download QR button (creates a download link)
- Toast notification: "URL shortened successfully!"

**Total time:** 50-100ms from click to result displayed.

## L.2 Complete Walkthrough: Clicking a Short Link (Redirect)

This walkthrough follows what happens when someone clicks `https://2goi.in/2Bq`.

**Step 1: Browser Request**
- User clicks the link (or types it in browser)
- Browser sends: `GET /2Bq` to server
- Includes headers: `User-Agent`, `Referer`, `X-Forwarded-For` (real IP)

**Step 2: Route Matching (main.py)**
- FastAPI checks routes in order:
  - `/api/health` → does not match
  - `/api/shorten` → does not match
  - `/api/links` → does not match
  - `/{short_code}` → MATCHES with `short_code = "2Bq"`

**Step 3: Route Guard (redirect.py)**
- Check: is `"2Bq"` in frontend routes? (`login`, `signup`, `dashboard`) → No
- Check: does `"2Bq"` start with `"api"`? → No
- Proceed with redirect logic

**Step 4: Redis Cache Check**
- `redis.get("url:2Bq")` → returns `"https://www.example.com/very/long/path?param=value"`
- **Cache HIT!** (3ms)

**Step 5: Send Redirect Response**
- Server sends HTTP 302 with `Location: https://www.example.com/very/long/path?param=value`
- Browser immediately navigates to the original URL

**Step 6: Background Click Logging (after response is sent)**
- `_log_click_background()` runs asynchronously
- Extracts User-Agent: `"Mozilla/5.0 ... Chrome/120"` → browser = `"Chrome"`, device = `"desktop"`
- Hashes IP: `SHA256("192.168.1.1")` → `"a1b2c3d4..."`
- Inserts click record into `clicks` table
- Upserts into `daily_click_stats` (increment today's count by 1)
- Increments `links.click_count` by 1

**Total time for user:** 3-5ms (cache hit) or 20-50ms (cache miss). Click logging adds zero wait time.

## L.3 Complete Walkthrough: Viewing Analytics

**Step 1:** User navigates to `/analytics/2Bq` from the dashboard
**Step 2:** React Router renders `AnalyticsPage.jsx` with `shortCode = "2Bq"`
**Step 3:** `useEffect` calls `getLinkAnalytics("2Bq", 30)` → `GET /api/analytics/2Bq?days=30`
**Step 4:** Backend verifies JWT token → extracts user_id
**Step 5:** Backend finds the link and checks ownership (`user_id` must match)
**Step 6:** Backend runs 4 database queries:
  - Total clicks: `SELECT COUNT(*) FROM clicks WHERE link_id = '...'`
  - Countries: `SELECT country, COUNT(*) ... GROUP BY country ORDER BY count DESC LIMIT 10`
  - Devices: `SELECT device_type, COUNT(*) ... GROUP BY device_type`
  - Browsers: `SELECT browser, COUNT(*) ... GROUP BY browser ORDER BY count DESC LIMIT 10`
  - Daily trend: `SELECT date, click_count FROM daily_click_stats WHERE link_id = '...' ORDER BY date LIMIT 30`
**Step 7:** Response:
```json
{
    "short_code": "2Bq",
    "total_clicks": 1523,
    "countries": [{"country": "IN", "count": 800}, {"country": "US", "count": 400}],
    "devices": [{"device_type": "mobile", "count": 900}, {"device_type": "desktop", "count": 623}],
    "browsers": [{"browser": "Chrome", "count": 700}, {"browser": "Safari", "count": 500}],
    "daily_clicks": [{"date": "2026-03-01", "count": 45}, {"date": "2026-03-02", "count": 67}]
}
```
**Step 8:** Frontend renders 4 charts:
  - Line chart for daily trend (Recharts `<LineChart>`)
  - Bar chart for countries (Recharts `<BarChart>` horizontal)
  - Pie chart for devices (Recharts `<PieChart>`)
  - Progress bars for browsers (custom CSS)

## L.4 Complete Walkthrough: Deleting a Link

**Step 1:** User clicks trash icon on dashboard → confirm dialog
**Step 2:** Frontend calls `DELETE /api/links/{link_id}` with JWT token
**Step 3:** Backend verifies ownership: `SELECT * FROM links WHERE id = :id AND user_id = :user_id`
**Step 4:** Soft delete: `link.is_active = False` → `db.commit()`
**Step 5:** Cache invalidation: `redis.delete("url:2Bq")` → removes cached URL
**Step 6:** Response: `204 No Content`
**Step 7:** Frontend refreshes the links list → deleted link disappears
**Step 8:** If someone clicks `2goi.in/2Bq` now:
  - Redis: key not found (was deleted)
  - Database: `is_active = False` → returns None
  - Result: **404 Not Found**

## L.5 Complete Walkthrough: User Signup and Login

**Signup flow:**
1. User fills email and password on signup page
2. Frontend calls `supabase.auth.signUp({ email, password })`
3. Supabase creates the user in its auth system
4. Supabase sends confirmation email via Resend SMTP (from `noreply@2goi.in`)
5. User checks email, clicks confirmation link
6. Supabase marks the email as confirmed
7. User can now log in

**Login flow:**
1. User enters email and password on login page
2. Frontend calls `supabase.auth.signInWithPassword({ email, password })`
3. Supabase verifies credentials
4. Supabase returns a JWT token (signed with ES256)
5. Frontend stores the token (Supabase JS handles this in localStorage)
6. `onAuthStateChange` fires → AuthContext updates `user` state
7. User is redirected to `/dashboard`
8. All subsequent API calls include the JWT in the `Authorization` header

**Google OAuth flow:**
1. User clicks "Continue with Google"
2. Frontend calls `supabase.auth.signInWithOAuth({ provider: 'google' })`
3. Browser redirects to Google login page
4. User enters Google credentials on Google's page (we never see the password)
5. Google redirects to Supabase's callback URL with an authorization code
6. Supabase exchanges the code for user profile information
7. Supabase creates or updates the user account
8. Supabase issues a JWT token
9. Browser redirects to `2goi.in/dashboard` with the session established


# Appendix M: Entity-Relationship Diagram (Text Format)

```
┌─────────────────────────────────────────────────┐
│                     USERS                        │
├─────────────────────────────────────────────────┤
│ id (UUID) ← Primary Key (from Supabase Auth)    │
│ email (VARCHAR 255) ← Unique                     │
│ plan (VARCHAR 20) ← Default: "free"              │
│ created_at (TIMESTAMPTZ) ← Auto                  │
└──────────────────────┬──────────────────────────┘
                       │
                       │ ONE user has MANY links
                       │
┌──────────────────────▼──────────────────────────┐
│                     LINKS                        │
├─────────────────────────────────────────────────┤
│ id (UUID) ← Primary Key                         │
│ sequence_id (BIGINT) ← Unique, auto-increment   │
│ original_url (TEXT) ← The long URL               │
│ short_code (VARCHAR 20) ← Unique, indexed        │
│ user_id (UUID) ← Foreign Key → users.id          │
│ click_count (INTEGER) ← Default: 0               │
│ is_active (BOOLEAN) ← Default: true              │
│ created_at (DATETIME) ← Auto                     │
│ expires_at (DATETIME) ← Optional                 │
└──────────┬──────────────────────┬───────────────┘
           │                      │
           │ ONE link has         │ ONE link has MANY
           │ MANY clicks          │ daily stat rows
           │                      │
┌──────────▼──────────┐  ┌───────▼────────────────┐
│       CLICKS         │  │   DAILY_CLICK_STATS     │
├─────────────────────┤  ├────────────────────────┤
│ id (UUID) ← PK      │  │ id (UUID) ← PK         │
│ link_id (UUID) ← FK │  │ link_id (UUID) ← FK    │
│ country (VARCHAR 10) │  │ date (DATE)             │
│ browser (VARCHAR 50) │  │ click_count (INTEGER)   │
│ device_type (20)     │  │                         │
│ referrer (2048)      │  │ UNIQUE(link_id, date)   │
│ ip_hash (VARCHAR 64) │  │ ← Enables upsert        │
│ clicked_at (DT) ← IX│  └────────────────────────┘
└─────────────────────┘

Relationships:
  users (1) ──────── (N) links        : One user owns many links
  links (1) ──────── (N) clicks       : One link has many click events
  links (1) ──────── (N) daily_stats  : One link has one stat row per day
```

**Key constraints:**
- `links.short_code` is UNIQUE and INDEXED → fast redirect lookups
- `links.sequence_id` uses a PostgreSQL SEQUENCE starting at 10000
- `daily_click_stats(link_id, date)` has a UNIQUE constraint → enables upsert
- `clicks.link_id` and `daily_click_stats.link_id` have ON DELETE CASCADE → when a link is hard-deleted, all its clicks and stats are automatically removed


# Appendix N: Sequence Diagrams (Text Format)

## N.1 URL Shortening Sequence

```
User          Frontend         Backend          PostgreSQL       Redis
 │               │                │                 │              │
 │  Paste URL    │                │                 │              │
 │──────────────>│                │                 │              │
 │               │ POST /api/     │                 │              │
 │               │  shorten       │                 │              │
 │               │───────────────>│                 │              │
 │               │                │ INSERT link     │              │
 │               │                │ (pending code)  │              │
 │               │                │────────────────>│              │
 │               │                │ sequence_id     │              │
 │               │                │<────────────────│              │
 │               │                │                 │              │
 │               │                │ encode_base62   │              │
 │               │                │ (10008 → "2Bq") │              │
 │               │                │                 │              │
 │               │                │ UPDATE code     │              │
 │               │                │────────────────>│              │
 │               │                │      OK         │              │
 │               │                │<────────────────│              │
 │               │                │                 │              │
 │               │                │ SET url:2Bq     │              │
 │               │                │ (cache prime)   │              │
 │               │                │────────────────────────────── >│
 │               │                │      OK         │              │
 │               │                │<──────────────────────────────│
 │               │                │                 │              │
 │               │                │ generate QR     │              │
 │               │                │ (in memory)     │              │
 │               │                │                 │              │
 │               │  JSON response │                 │              │
 │               │  (short_url,   │                 │              │
 │               │   qr_code)     │                 │              │
 │               │<───────────────│                 │              │
 │  Show result  │                │                 │              │
 │<──────────────│                │                 │              │
```

## N.2 Redirect Sequence (Cache Hit)

```
Visitor        Browser          Backend           Redis          PostgreSQL
 │               │                │                 │              │
 │  Click link   │                │                 │              │
 │──────────────>│                │                 │              │
 │               │ GET /2Bq       │                 │              │
 │               │───────────────>│                 │              │
 │               │                │ GET url:2Bq     │              │
 │               │                │────────────────>│              │
 │               │                │ "https://..."   │              │
 │               │                │<────────────────│              │
 │               │                │                 │              │
 │               │ 302 Redirect   │                 │              │
 │               │<───────────────│                 │              │
 │  See target   │                │                 │              │
 │  page         │                │                 │              │
 │<──────────────│                │                 │              │
 │               │                │                 │              │
 │               │                │ [BACKGROUND]    │              │
 │               │                │ log click       │              │
 │               │                │────────────────────────────── >│
 │               │                │ INSERT click    │              │
 │               │                │ UPSERT daily    │              │
 │               │                │ INCREMENT count │              │
```

## N.3 Google OAuth Sequence

```
User          Frontend         Supabase          Google         Backend
 │               │                │                │              │
 │  Click        │                │                │              │
 │  "Google"     │                │                │              │
 │──────────────>│                │                │              │
 │               │ signInWithOAuth│                │              │
 │               │───────────────>│                │              │
 │               │                │ Redirect to    │              │
 │               │                │ Google login   │              │
 │               │<───────────────│                │              │
 │               │                │                │              │
 │  Enter Google │                │                │              │
 │  credentials  │                │                │              │
 │───────────────────────────────────────────────>│              │
 │               │                │                │              │
 │               │                │  Auth code     │              │
 │               │                │<───────────────│              │
 │               │                │                │              │
 │               │                │ Exchange code  │              │
 │               │                │ for user info  │              │
 │               │                │───────────────>│              │
 │               │                │ email, name    │              │
 │               │                │<───────────────│              │
 │               │                │                │              │
 │               │ JWT token      │                │              │
 │               │<───────────────│                │              │
 │               │                │                │              │
 │               │ API call with  │                │              │
 │               │ JWT token      │                │              │
 │               │──────────────────────────────────────────────>│
 │               │                │                │              │
 │               │                │                │  Verify JWT  │
 │               │                │                │  via JWKS    │
 │               │                │                │  Create user │
 │               │                │                │  if new      │
 │               │                │                │              │
 │  Dashboard    │                │                │              │
 │<──────────────│                │                │              │
```


# Appendix O: Additional Interview Questions (Advanced)

## O.1 System Design Questions

### Q: Draw the system architecture of your URL shortener.

**A:** (Refer to the diagram in Section 7 and Appendix N)

```
┌──────────┐     ┌───────────────────────────────────┐
│  Browser  │────>│        Render (Docker)             │
│           │<────│                                     │
└──────────┘     │  ┌───────────────────────────────┐ │
                 │  │  Gunicorn (4 Uvicorn workers)  │ │
                 │  │                                 │ │
                 │  │  ┌───────────┐  ┌───────────┐  │ │
                 │  │  │ FastAPI   │  │ React SPA  │  │ │
                 │  │  │ (API +    │  │ (static    │  │ │
                 │  │  │  redirect)│  │  files)    │  │ │
                 │  │  └─────┬─────┘  └───────────┘  │ │
                 │  └────────┼────────────────────────┘ │
                 │           │                           │
                 │    ┌──────┴──────┐                    │
                 │    │             │                    │
                 │  ┌─▼──┐     ┌───▼────────┐           │
                 │  │Redis│     │ PostgreSQL  │           │
                 │  │(25MB│     │ (Supabase)  │           │
                 │  │cache)│     │ 500MB DB    │           │
                 │  └─────┘     └────────────┘           │
                 └───────────────────────────────────────┘
```

### Q: What is the difference between vertical and horizontal scaling?

**A:**
- **Vertical scaling (scale up):** Make one server bigger — more CPU, more RAM. Example: upgrade from 2GB RAM to 16GB RAM. Simple but has a limit (you can't make one server infinitely powerful).
- **Horizontal scaling (scale out):** Add more servers. Example: run 10 identical servers behind a load balancer. No theoretical limit, but requires the application to be stateless.

Our app supports horizontal scaling because all state is in PostgreSQL and Redis, not in the server's memory. Any server can handle any request.

### Q: What is the CAP theorem and how does it apply?

**A:** The CAP theorem states that a distributed system can only guarantee two of three properties:
- **Consistency:** Every read returns the most recent write
- **Availability:** Every request receives a response
- **Partition tolerance:** The system works despite network failures

Our system prioritizes **Availability + Partition tolerance (AP)** for redirects:
- If Redis is down, we fall back to the database (available but possibly slower)
- If the database is down, cached redirects still work (available but stale data possible)
- For link creation, we prioritize **Consistency** — the database is the source of truth

### Q: What is connection pooling and how does it work in your project?

**A:** Connection pooling keeps a set of pre-established database connections ready to use.

Our configuration (`database.py`):
- `pool_size = 20` → Keep 20 connections always ready
- `max_overflow = 10` → Allow 10 extra during traffic spikes (total max: 30)
- `pool_pre_ping = True` → Before using a connection, check if it's still alive (sends `SELECT 1`)
- `pool_recycle = 300` → Replace connections older than 5 minutes (avoids stale connections)

Without pooling: each request takes 50-100ms just to connect to the database.
With pooling: each request borrows a connection instantly (0ms overhead).

### Q: What is the difference between synchronous and asynchronous programming?

**A:** Simple analogy:

**Synchronous (blocking):**
- You order food at a restaurant
- You stand at the counter waiting until your food is ready
- You cannot do anything else while waiting

**Asynchronous (non-blocking):**
- You order food at a restaurant
- You take a buzzer and sit down
- While waiting, you check your phone, talk to friends
- The buzzer rings when food is ready

In our code:
```python
# Async: While waiting for Redis, the worker can handle other requests
cached_url = await redis.get(f"url:{short_code}")

# Async: While waiting for DB, the worker can handle other requests
link = await get_link_by_code(db, short_code)
```

One async worker can handle hundreds of concurrent requests because it never sits idle waiting.

## O.2 Additional Concept Questions

### Q: What is User-Agent parsing and why do you do it?

**A:** The User-Agent is a string the browser sends with every request. Example:
```
Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1
```

We parse this string using the `user-agents` Python library to extract:
- **Browser:** Safari
- **Device type:** mobile (because it contains "iPhone")

This data powers the analytics charts (device pie chart and browser progress bars).

### Q: What is SSL/TLS and why is it important?

**A:** SSL/TLS encrypts all data between the browser and server. Without it:
- Anyone on the same network can read the URLs being shortened
- JWT tokens could be intercepted (session hijacking)
- Browsers show "Not Secure" warning

Our setup:
- Render provides free SSL certificates (auto-renewed via Let's Encrypt)
- All HTTP traffic is redirected to HTTPS
- Database connections also use SSL (configured in `database.py` with `ssl_context`)

### Q: What is rate limiting and how does yours work?

**A:** Rate limiting restricts how many requests a user can make in a time period.

**How ours works:**
1. SlowAPI middleware intercepts every request
2. Extracts the client's real IP from `X-Forwarded-For` header
3. Checks: has this IP made more than 100 requests in the last minute?
4. If yes: return `429 Too Many Requests`
5. If no: allow the request through

**Why it matters:**
- **Without rate limiting:** A bot could create millions of links, filling our database
- **Without rate limiting:** An attacker could make millions of requests per second (DDoS)
- **With rate limiting:** Each IP is limited to 100 requests/minute, preventing abuse

### Q: What is the difference between HTTP 301 and 302 redirect?

**A:**
- **301 (Permanent Redirect):** The browser caches this redirect forever. Next time the user visits the short URL, the browser goes directly to the target WITHOUT contacting our server. This means we CANNOT track that click.
- **302 (Temporary Redirect):** The browser does NOT cache this. Every time the user clicks the short URL, the browser contacts our server first. This means we CAN track every click.

We use 302 because:
1. We need to track every click for analytics
2. The link might expire (we need to check expiration)
3. The link might be deleted (we need to return 404)

### Q: What are environment variables and why do you use them?

**A:** Environment variables are key-value pairs set on the server, NOT in the code.

**Why not hardcode values in the code?**
1. **Security:** Database passwords and API keys would be visible on GitHub
2. **Flexibility:** Different values for development vs production (different database URLs)
3. **12-Factor App principle:** Configuration should be separate from code

**Example:**
```bash
# In Render dashboard (production):
DATABASE_URL=postgresql+asyncpg://real-user:real-password@supabase-host:5432/postgres

# In local .env file (development):
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twogoi
```

Same code, different configuration. No code changes needed between environments.

### Q: What is Pydantic and how do you use it?

**A:** Pydantic is a Python library for data validation using type hints.

**We use it in two ways:**

1. **API request/response validation (schemas/):**
```python
class LinkCreate(BaseModel):
    url: HttpUrl           # Must be a valid HTTP/HTTPS URL
    custom_alias: str = None  # Optional
    expires_in: int = None    # Optional, in seconds
```
If a user sends `{"url": "not-a-url"}`, Pydantic automatically returns `422 Unprocessable Entity` before our code even runs.

2. **Configuration management (config.py):**
```python
class Settings(BaseSettings):
    DATABASE_URL: str = "default-value"
    REDIS_URL: str = "redis://localhost:6379"
```
Pydantic automatically reads from environment variables and validates their types.

### Q: What is a reverse proxy and how does Render use it?

**A:** A reverse proxy sits between the internet and your application. It receives all incoming requests and forwards them to the application.

Render's reverse proxy:
1. Handles SSL termination (encrypts/decrypts HTTPS)
2. Adds `X-Forwarded-For` header with the client's real IP
3. Load balances across multiple instances (on paid plans)
4. Handles health checks

That is why we read the IP from `X-Forwarded-For` instead of `request.client.host` — the direct client is Render's proxy, not the actual user.


# Appendix P: Project Timeline

| Week | Tasks Completed |
|------|----------------|
| Week 1 | Project planning, tech stack selection, database schema design, Supabase setup |
| Week 2 | Backend development — FastAPI app, models, Base62 encoding, Redis caching, authentication |
| Week 3 | Frontend development — React pages, TailwindCSS styling, Recharts analytics, responsive design |
| Week 4 | Integration — API + frontend, Docker setup, Render deployment, custom domain, SSL |
| Week 5 | Production hardening — Google OAuth, Resend email, SEO, error handling, documentation |
| Week 6 | Testing, documentation (README, DOCUMENTATION, SETUP_GUIDE), academic report |


# Appendix Q: Key Metrics and Numbers

| Metric | Value | Explanation |
|--------|-------|-------------|
| Redirect (cache hit) | 3-5 ms | Redis → 302 response |
| Redirect (cache miss) | 20-50 ms | PostgreSQL → Redis → 302 response |
| Link creation | 50-100 ms | DB insert + Base62 + cache prime + QR |
| Max short codes (6 chars) | 56.8 billion | 62^6 possible combinations |
| Sequence start | 10000 | Guarantees 3+ character codes |
| Redis capacity | ~170,000 URLs | 25MB / ~150 bytes per entry |
| DB connection pool | 20 + 10 overflow | Max 30 concurrent DB connections |
| Rate limit (anon) | 100/minute | Per IP address |
| Rate limit (auth) | 1000/minute | Per IP address |
| Docker image size | ~300 MB | Multi-stage build optimization |
| Monthly cost | ~₹67 | Domain only — everything else is free |
| Total code lines | ~2,500 | Backend ~1,100 + Frontend ~1,400 |
| Number of API endpoints | 6 | shorten, redirect, links, delete, analytics, health |
| Number of database tables | 4 | users, links, clicks, daily_click_stats |
| Number of indexes | 5 | short_code, user_id, link_id, clicked_at, link_date |


---

*Built by Badri Pamisetty — https://github.com/Badri-2915/2goi*
