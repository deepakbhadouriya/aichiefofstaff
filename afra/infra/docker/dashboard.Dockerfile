FROM node:20-alpine

WORKDIR /app

COPY apps/dashboard/package.json ./
RUN npm install

COPY apps/dashboard ./

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
