# Use official nginx image
FROM nginx:stable-alpine

# Copy only the browser build
COPY ./dist/idear/browser /usr/share/nginx/html

# Replace default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
