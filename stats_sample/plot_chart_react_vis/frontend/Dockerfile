FROM node:12.13.0

WORKDIR /frontend
COPY . /frontend
RUN yarn build

EXPOSE 3000

CMD ["yarn", "start"]
