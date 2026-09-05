<?php

namespace Tests\Feature;

use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class PagesTest extends TestCase
{
    /**
     * Every page this app serves should render without error. There's no
     * database or auth here — that all lives in the Django API — so this
     * is just confirming each Blade view compiles and returns 200.
     */
    public static function routes(): array
    {
        return [
            ['/'], ['/about'], ['/academics'], ['/student-life'],
            ['/admissions'], ['/news'], ['/contact'], ['/application'],
            ['/applicant-portal'], ['/student-portal'],
            ['/admissions-admin'], ['/dashboard-admin'],
        ];
    }

    #[DataProvider('routes')]
    public function test_page_renders(string $uri): void
    {
        $this->get($uri)->assertStatus(200);
    }

    // Static assets (styles.css, portal.js, og.png, ...) aren't routed
    // through Laravel at all in production (the web server / `artisan
    // serve` serves them straight from public/), and PHPUnit's HTTP test
    // client doesn't emulate that passthrough — so there's nothing
    // meaningful to assert on here via Feature tests. Verified manually
    // instead: `php artisan serve` + curl against each asset path.
}
