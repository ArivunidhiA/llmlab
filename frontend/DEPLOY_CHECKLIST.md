# LLMLab Frontend - Deployment Checklist

Complete checklist before deploying to production.

## Pre-Deployment Setup

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env.production`
- [ ] Set `NEXT_PUBLIC_API_URL` to your backend API
- [ ] Verify API endpoint is accessible
- [ ] Test authentication endpoints
- [ ] Confirm CORS headers are set on backend

### 2. Dependencies
- [ ] Run `npm install`
- [ ] Run `npm audit` and fix vulnerabilities
- [ ] Check Node.js version (18+)
- [ ] Verify all dependencies in package.json

### 3. Code Quality
- [ ] Run `npm run type-check` - No errors
- [ ] Run `npm run lint` - No errors
- [ ] Run `npm test` - All tests passing
- [ ] Run `npm run build` - Successful build

### 4. Testing
- [ ] Test all pages load correctly
- [ ] Test authentication flow
  - [ ] Sign up creates account
  - [ ] Login works
  - [ ] Logout clears session
- [ ] Test dashboard loads with real data
- [ ] Test API key management
- [ ] Test budget alerts
- [ ] Test dark mode on all pages
- [ ] Test mobile responsiveness
- [ ] Test browser compatibility

### 5. Performance
- [ ] Lighthouse score > 90
- [ ] Check build size with `npm run build`
- [ ] Verify images are optimized
- [ ] Check font loading performance
- [ ] Verify no console warnings/errors

### 6. Security
- [ ] No API keys in code
- [ ] No secrets in `.env.example`
- [ ] HTTPS enabled on production
- [ ] CSP headers configured
- [ ] CORS properly configured
- [ ] Rate limiting on backend
- [ ] Input validation working
- [ ] XSS protection in place

### 7. Accessibility
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets standards
- [ ] Form labels properly associated

### 8. Analytics & Monitoring
- [ ] Analytics configured (optional)
- [ ] Error tracking setup
- [ ] Performance monitoring
- [ ] Health check endpoint
- [ ] Logging configured

## Deployment Options

### Option A: Vercel (Recommended)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy
vercel --prod

# 4. Configure environment variables in dashboard
# 5. Verify deployment at vercel.com dashboard
```

**Checklist**:
- [ ] Vercel account created
- [ ] GitHub repository connected
- [ ] Environment variables set in Vercel dashboard
- [ ] Auto-deployments enabled
- [ ] Domain configured (optional)
- [ ] SSL certificate auto-renewed

### Option B: Docker

```bash
# 1. Create Dockerfile (already provided)
# 2. Build image
docker build -t llmlab-frontend:latest .

# 3. Test locally
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://your-api.com \
  llmlab-frontend:latest

# 4. Push to registry
docker tag llmlab-frontend:latest your-registry/llmlab-frontend:latest
docker push your-registry/llmlab-frontend:latest

# 5. Deploy to your platform (Kubernetes, Docker Swarm, etc.)
```

**Checklist**:
- [ ] Docker installed locally
- [ ] Docker registry account (Docker Hub, ECR, GCR, etc.)
- [ ] Dockerfile tested locally
- [ ] Environment variables in .env
- [ ] Docker image built successfully
- [ ] Image pushed to registry
- [ ] Container orchestration configured

### Option C: Traditional VPS/Server

```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Clone repository
git clone https://github.com/your-org/llmlab.git
cd llmlab/frontend

# 3. Install Node.js (if not present)
curl https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18

# 4. Install dependencies
npm install

# 5. Build
npm run build

# 6. Setup PM2 for process management
npm install -g pm2
pm2 start "npm start" --name "llmlab-frontend"
pm2 save
pm2 startup

# 7. Setup Nginx reverse proxy
# Create /etc/nginx/sites-available/llmlab
# Point to localhost:3000

# 8. Setup SSL with Let's Encrypt
sudo certbot certonly --standalone -d your-domain.com

# 9. Start Nginx
sudo systemctl start nginx
```

**Checklist**:
- [ ] VPS/Server access confirmed
- [ ] Node.js 18+ installed
- [ ] PM2 process manager installed
- [ ] Nginx installed and configured
- [ ] SSL certificate obtained
- [ ] Firewall rules configured
- [ ] Application deployed
- [ ] Auto-restart configured

## Post-Deployment Verification

### 1. Frontend Checks
```bash
# Navigate to your deployment URL
curl https://your-domain.com/

# Check status codes
curl -I https://your-domain.com/
# Should return 200 OK

curl -I https://your-domain.com/dashboard
# Should redirect to login (302)
```

**Checklist**:
- [ ] Homepage loads (HTTP 200)
- [ ] All pages accessible
- [ ] Redirects working
- [ ] Assets loading (CSS, JS, fonts)
- [ ] Dark mode works
- [ ] Mobile responsive

### 2. API Integration
```bash
# Test authentication
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Should return token or error
```

**Checklist**:
- [ ] API endpoints accessible
- [ ] Authentication working
- [ ] Dashboard data loading
- [ ] API keys creation working
- [ ] Budget alerts functioning

### 3. Performance
```bash
# Run Lighthouse audit
npm install -g lighthouse
lighthouse https://your-domain.com/ --chrome-flags="--headless"
```

**Checklist**:
- [ ] Lighthouse score acceptable
- [ ] Page load time < 3 seconds
- [ ] No console errors
- [ ] No network errors
- [ ] Images optimized

### 4. Monitoring
**Checklist**:
- [ ] Error tracking working
- [ ] Analytics capturing events
- [ ] Uptime monitoring active
- [ ] Alert notifications configured
- [ ] Logs being collected

## Rollback Plan

If something goes wrong:

### For Vercel
```bash
# Revert to previous deployment
vercel rollback
```

### For Docker
```bash
# Revert to previous image
docker run -p 3000:3000 \
  llmlab-frontend:previous-tag
```

### For Traditional Server
```bash
# Revert git changes
git revert HEAD
npm install
npm run build
pm2 restart llmlab-frontend
```

## Monitoring & Maintenance

### Daily Checks
- [ ] Application is running
- [ ] No error spike in logs
- [ ] API response times normal
- [ ] User login working

### Weekly Checks
- [ ] Review error logs
- [ ] Check performance metrics
- [ ] Verify backups
- [ ] Update dependencies (if safe)

### Monthly Checks
- [ ] Security audit
- [ ] Performance optimization
- [ ] Cost review (if using cloud)
- [ ] User feedback review

## Incident Response

If issues occur:

1. **Page Won't Load**
   - Check server is running
   - Check network connectivity
   - Review error logs
   - Restart application if needed

2. **API Integration Failed**
   - Verify API URL in environment
   - Check API server is running
   - Review CORS configuration
   - Check authentication token

3. **High CPU Usage**
   - Check for infinite loops
   - Review memory usage
   - Check polling intervals
   - Reduce concurrent connections

4. **Users Locked Out**
   - Verify authentication system
   - Check database connectivity
   - Review session configuration
   - Clear browser cache

## Cleanup & Optimization

After deployment is live:

### 1. Code Cleanup
- [ ] Remove console.log() statements
- [ ] Remove debug code
- [ ] Remove unused imports
- [ ] Optimize bundle size

### 2. Asset Optimization
- [ ] Compress images
- [ ] Minify CSS/JS (automatic with build)
- [ ] Optimize fonts (preload critical)
- [ ] Remove unused fonts

### 3. Performance Tuning
- [ ] Enable gzip compression
- [ ] Setup caching headers
- [ ] Enable CDN (if using cloud)
- [ ] Optimize database queries

### 4. Documentation
- [ ] Update deployment docs
- [ ] Document environment setup
- [ ] Create runbooks for common tasks
- [ ] Document incident response

## Sign-Off Checklist

Before considering deployment complete:

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Team trained on deployment
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Client approval obtained
- [ ] Post-deployment monitoring scheduled

## Useful Commands

```bash
# Development
npm run dev              # Start dev server
npm test                # Run tests
npm run type-check      # Check types
npm run lint            # Lint code

# Production
npm run build           # Build for production
npm start              # Start production server

# Debugging
npm run dev -- --debug  # Debug mode
npm test -- --verbose   # Verbose test output

# Cleaning
rm -rf .next            # Clear build cache
rm -rf node_modules     # Clear dependencies
npm install             # Reinstall dependencies
```

## Emergency Contacts

- **Deployment Lead**: [Name/Contact]
- **Backend Team**: [Contact Info]
- **DevOps/Infra**: [Contact Info]
- **Support Team**: [Contact Info]

## Deployment History

| Date | Version | Environment | Status | Notes |
|------|---------|-------------|--------|-------|
| 2024-02-09 | 0.1.0 | Staging | Ready | Initial release |
| | | Production | Pending | Awaiting approval |

---

**Last Updated**: February 9, 2024
**Maintained By**: Frontend Team
**Next Review**: February 16, 2024
