# Railway Deployment Instructions

## Environment Variables to Set in Railway Dashboard:

1. GROQ_API_KEY=your_actual_groq_api_key_here
2. SECRET_KEY=generate-a-secure-random-string-for-production
3. DEBUG=False
4. LOG_LEVEL=INFO
5. UPLOAD_DIR=./uploads
6. MAX_FILE_SIZE=50000000

## Optional Database (if needed later):
DATABASE_URL=postgresql://username:password@host:port/database

## To deploy:
1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Set the environment variables above
4. Railway will auto-deploy!

## Your app will be available at:
https://your-app-name.railway.app