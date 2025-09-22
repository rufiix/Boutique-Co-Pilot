# Etap 1: Budowanie aplikacji
FROM golang:1.22-alpine AS builder
WORKDIR /usr/src/app
# Kopiujemy tylko kod frontendu, a nie całe repozytorium
COPY src/frontend/ .
# Pobieramy zależności i budujemy
RUN go mod download
RUN CGO_ENABLED=0 go build -o /go/bin/frontend .

# Etap 2: Stworzenie finalnego, lekkiego obrazu
FROM gcr.io/distroless/static-debian12
WORKDIR /usr/src/app
# Kopiujemy tylko skompilowaną aplikację i potrzebne pliki z etapu budowania
COPY --from=builder /go/bin/frontend .
COPY --from=builder /usr/src/app/static ./static
COPY --from=builder /usr/src/app/templates ./templates
EXPOSE 8080
ENTRYPOINT ["/usr/src/app/frontend"]