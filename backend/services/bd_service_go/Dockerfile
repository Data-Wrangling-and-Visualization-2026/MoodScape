# Этап сборки
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Копируем только файлы зависимостей для кеширования слоёв
COPY go.mod go.sum ./
RUN go mod download

# Копируем весь исходный код
COPY . .

# Собираем статический бинарник
RUN CGO_ENABLED=0 GOOS=linux go build -o /trackservice ./cmd/api

# Финальный образ
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /trackservice .

EXPOSE 8004

CMD ["./trackservice"]