# приватный ключ
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out /tmp/auth_jwt_private.pem

# публичный ключ
openssl rsa -in /tmp/auth_jwt_private.pem -pubout -out /tmp/auth_jwt_public.pem

```shell
PRIVATE_KEY=$(awk '{printf "%s\\n", $0}' /tmp/auth_jwt_private.pem)
PUBLIC_KEY=$(awk '{printf "%s\\n", $0}' /tmp/auth_jwt_public.pem)

cat > auth-service/.env <<EOF
JWT_ISSUER=auth-service
JWT_AUDIENCE=user-children-service
JWT_ALGORITHMS=RS256
JWT_PRIVATE_KEY_PEM=${PRIVATE_KEY}
JWT_PUBLIC_KEY_PEM=${PUBLIC_KEY}
JWT_ACCESS_TTL_SECONDS=900
JWT_REFRESH_TTL_SECONDS=604800
EOF
```