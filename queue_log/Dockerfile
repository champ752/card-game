FROM golang:1.16.0 AS builder
COPY . ./
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix nocgo -o /server .

FROM scratch
COPY --from=builder ./server ./
COPY --from=builder ./config ./config
EXPOSE 8080
ENTRYPOINT ["./server"]