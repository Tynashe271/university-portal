# Render has no native PHP runtime (see README.md#deploying-it-for-real),
# so this app deploys as a Docker web service instead of Render's usual
# runtime: python/node/etc.
#
# This runs `php artisan serve` rather than a real nginx+php-fpm stack.
# That's fine for what this app actually is — a handful of Blade views
# with no database and no heavy traffic — but Laravel's own docs are
# explicit that `serve` "should never be used in a production environment"
# for anything with real concurrency needs. If this ever needs to handle
# real traffic, swap this out for an nginx+php-fpm image instead (Render's
# own guide: https://render.com/docs/deploy-php-laravel-docker).
FROM php:8.3-cli-alpine

RUN apk add --no-cache git unzip icu-dev oniguruma-dev libzip-dev sqlite-dev \
    && docker-php-ext-install pdo pdo_sqlite mbstring bcmath ctype fileinfo intl

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app

# Install dependencies first so this layer is cached across builds that
# don't touch composer.json/composer.lock.
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --no-interaction --prefer-dist --optimize-autoloader

COPY . .
RUN composer dump-autoload --optimize

EXPOSE 10000
# APP_KEY needs a specific format (base64:<32 exact bytes>) that Render's
# generic `generateValue` can't produce (see render.yaml) — generate one
# fresh on boot when it's not set. A new key each restart is fine here:
# this app has no real sessions/auth of its own for it to invalidate
# (that's all in the Django backend), it only affects Laravel's own
# cookie/session encryption.
CMD ["sh", "-c", "export APP_KEY=${APP_KEY:-$(php artisan key:generate --show)} && php artisan serve --host=0.0.0.0 --port=${PORT:-10000}"]
